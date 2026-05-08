"""
UpdateContractPhase MCP Tool with comprehensive security, compliance, and audit logging.

This example demonstrates:
- Token validation and expiration checks
- OBO (On-Behalf-Of) token exchange for delegated access
- DLP (Data Loss Prevention) content checks
- Structured audit logging
- Comprehensive error handling
- Type-safe parameter validation
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field, validator, BaseModel
from functools import wraps


# ============================================================================
# Configuration and Setup
# ============================================================================

# Initialize MCP server
mcp = FastMCP("contract-manager")

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

# Audit log handler (in production, write to centralized logging service)
audit_handler = logging.FileHandler("audit.log")
audit_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)
audit_logger.addHandler(audit_handler)

# Configuration from environment
ACCESS_TOKEN_LIFETIME = int(os.environ.get("ACCESS_TOKEN_LIFETIME", 3600))  # 1 hour
OBO_SCOPES = os.environ.get("OBO_SCOPES", "contract:write audit:read").split()
DLP_SENSITIVE_FIELDS = [
    "ssn",
    "tax_id",
    "bank_account",
    "credit_card",
    "api_key",
    "password",
]


# ============================================================================
# Models and Enums
# ============================================================================


class ContractPhase(str, Enum):
    """Valid contract phases."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    EXECUTED = "executed"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TokenInfo(BaseModel):
    """Structure for validated token information."""

    token: str
    subject: str  # User ID (sub claim)
    issued_at: datetime
    expires_at: datetime
    scopes: list[str]
    obo_chain: list[str] = []  # Chain of on-behalf-of delegations


class UpdateContractPhaseRequest(BaseModel):
    """Validated request parameters with type safety."""

    contract_id: str = Field(
        description="Unique identifier for the contract",
        pattern=r"^[A-Z0-9]{8,}$",  # Example: alphanumeric, min 8 chars
    )
    new_phase: ContractPhase = Field(description="Target contract phase")
    reason: str = Field(
        description="Business reason for the phase change",
        min_length=10,
        max_length=500,
    )
    actor_token: str = Field(description="Bearer token of the user making the change")
    obo_token: Optional[str] = Field(
        default=None,
        description="Optional OBO token if acting on behalf of another user",
    )
    additional_notes: Optional[str] = Field(
        default=None, description="Additional context or notes", max_length=1000
    )

    @validator("contract_id")
    def validate_contract_id(cls, v):
        if not v or len(v) < 8:
            raise ValueError("contract_id must be at least 8 alphanumeric characters")
        return v.upper()

    @validator("reason")
    def validate_reason(cls, v):
        # DLP: check for sensitive patterns in reason field
        for pattern in DLP_SENSITIVE_FIELDS:
            if pattern.lower() in v.lower():
                raise ValueError(f"Sensitive field pattern detected: {pattern}")
        return v


# ============================================================================
# Token Management and Validation
# ============================================================================


def validate_token(token: str) -> TokenInfo:
    """
    Validate JWT token and return token info.

    In production, this would verify the signature with the auth server's public key.
    Here we simulate validation.

    Args:
        token: Bearer token to validate

    Returns:
        TokenInfo with extracted claims

    Raises:
        ValueError: If token is invalid, expired, or malformed
    """
    if not token or not token.startswith("Bearer "):
        raise ValueError("Invalid token format. Expected 'Bearer <token>'")

    try:
        # Remove "Bearer " prefix
        token_part = token.replace("Bearer ", "")

        # In production: verify signature with auth server
        # decoded = jwt.decode(token_part, public_key, algorithms=["RS256"])
        # For this example, simulate a valid token decode
        decoded = {
            "sub": "user-12345",  # Subject (user ID)
            "scope": "contract:write audit:read",
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        issued_at = datetime.fromtimestamp(decoded["iat"])
        expires_at = datetime.fromtimestamp(decoded["exp"])

        # Check expiration
        if datetime.utcnow() > expires_at:
            raise ValueError("Token has expired")

        # Validate required scopes
        token_scopes = decoded.get("scope", "").split()
        if "contract:write" not in token_scopes:
            raise ValueError("Token lacks required 'contract:write' scope")

        return TokenInfo(
            token=token_part,
            subject=decoded["sub"],
            issued_at=issued_at,
            expires_at=expires_at,
            scopes=token_scopes,
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode token: {e}")
    except KeyError as e:
        raise ValueError(f"Token missing required claim: {e}")


def exchange_obo_token(
    actor_token: str, obo_token: str, actor_info: TokenInfo
) -> TokenInfo:
    """
    Exchange an On-Behalf-Of token for delegated access.

    Validates that the actor has permission to use the delegated token
    and constructs the delegation chain for audit purposes.

    Args:
        actor_token: The actor's own token
        obo_token: The token being used on behalf of another party
        actor_info: Validated actor token info

    Returns:
        TokenInfo for the OBO context

    Raises:
        ValueError: If OBO exchange is not permitted
    """
    # Validate actor is permitted to use OBO
    if "delegation" not in actor_info.scopes and "admin" not in actor_info.scopes:
        raise ValueError("Token does not have permission for on-behalf-of exchanges")

    try:
        # In production: verify OBO token with auth server
        obo_info = validate_token(obo_token)

        # Build delegation chain: [original_actor, delegate1, delegate2, ...]
        obo_chain = actor_info.obo_chain + [actor_info.subject]

        return TokenInfo(
            token=obo_info.token,
            subject=obo_info.subject,
            issued_at=obo_info.issued_at,
            expires_at=obo_info.expires_at,
            scopes=obo_info.scopes,
            obo_chain=obo_chain,
        )
    except ValueError as e:
        raise ValueError(f"OBO token exchange failed: {e}")


# ============================================================================
# DLP (Data Loss Prevention) Checks
# ============================================================================


class DLPCheckResult(BaseModel):
    """Result of DLP content scan."""

    passed: bool
    violations: list[str] = []
    flagged_fields: list[str] = []


def check_dlp_content(
    content: str, sensitive_fields: list[str] = None
) -> DLPCheckResult:
    """
    Check content for sensitive data patterns (PII, credentials, etc.).

    In production, this would integrate with a data loss prevention service
    or pattern detection engine.

    Args:
        content: Text content to scan
        sensitive_fields: List of field patterns to check for

    Returns:
        DLPCheckResult with violations if any sensitive patterns detected
    """
    if not sensitive_fields:
        sensitive_fields = DLP_SENSITIVE_FIELDS

    violations = []
    flagged_fields = []

    for field in sensitive_fields:
        # Check for field name mentions (e.g., "ssn:", "SSN=")
        field_pattern_lower = field.lower()
        if field_pattern_lower in content.lower():
            violations.append(f"Potential sensitive field reference: {field}")
            flagged_fields.append(field)

    return DLPCheckResult(
        passed=len(violations) == 0,
        violations=violations,
        flagged_fields=flagged_fields,
    )


# ============================================================================
# Audit Logging
# ============================================================================


def log_audit_event(
    event_type: str,
    contract_id: str,
    actor_info: TokenInfo,
    action: str,
    result: str,
    metadata: dict = None,
):
    """
    Log a structured audit event for compliance and accountability.

    Args:
        event_type: Type of event (e.g., 'CONTRACT_UPDATE', 'TOKEN_VALIDATION_FAILED')
        contract_id: ID of affected contract
        actor_info: TokenInfo of the actor
        action: Description of the action taken
        result: Result of the action ('SUCCESS', 'FAILURE', 'BLOCKED')
        metadata: Additional context information
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "contract_id": contract_id,
        "actor": actor_info.subject,
        "actor_scopes": actor_info.scopes,
        "delegation_chain": actor_info.obo_chain,
        "action": action,
        "result": result,
        "metadata": metadata or {},
    }

    # Log to audit logger
    audit_logger.info(json.dumps(audit_entry))
    logger.info(f"Audit event: {event_type} - {action} - {result}")


def audit_log_decorator(event_type: str):
    """Decorator to automatically log critical operations."""

    def decorator(func):
        @wraps(func)
        async def wrapper(
            contract_id: str,
            actor_info: TokenInfo,
            *args,
            **kwargs,
        ):
            try:
                result = await func(contract_id, actor_info, *args, **kwargs)
                log_audit_event(
                    event_type=event_type,
                    contract_id=contract_id,
                    actor_info=actor_info,
                    action=func.__name__,
                    result="SUCCESS",
                    metadata={"result_summary": str(result)[:200]},
                )
                return result
            except Exception as e:
                log_audit_event(
                    event_type=event_type,
                    contract_id=contract_id,
                    actor_info=actor_info,
                    action=func.__name__,
                    result="FAILURE",
                    metadata={"error": str(e)},
                )
                raise

        return wrapper

    return decorator


# ============================================================================
# Core Business Logic
# ============================================================================


async def update_contract_phase_internal(
    contract_id: str,
    new_phase: ContractPhase,
    reason: str,
    actor_info: TokenInfo,
    notes: Optional[str] = None,
) -> dict:
    """
    Update contract phase with all validations applied.

    Args:
        contract_id: Contract ID to update
        new_phase: Target phase
        reason: Business reason for change
        actor_info: Validated actor token info
        notes: Optional additional notes

    Returns:
        Dictionary with update result

    Raises:
        ValueError: If validation fails
        Exception: If API call fails
    """
    # In production: verify contract exists and actor has access
    # Here we simulate the database operation
    logger.info(f"Updating contract {contract_id} to phase {new_phase}")

    # Simulate contract state validation
    # (check current phase allows transition to new_phase)
    valid_transitions = {
        "draft": ["review", "archived"],
        "review": ["approved", "draft", "archived"],
        "approved": ["executed", "review"],
        "executed": ["completed"],
        "completed": ["archived"],
        "archived": [],
    }

    # In production: fetch current phase from database
    current_phase = "draft"  # simulated

    if new_phase.value not in valid_transitions.get(current_phase, []):
        raise ValueError(
            f"Invalid transition from {current_phase} to {new_phase.value}"
        )

    # Simulate API call to contract service
    update_payload = {
        "contract_id": contract_id,
        "new_phase": new_phase.value,
        "reason": reason,
        "updated_by": actor_info.subject,
        "updated_at": datetime.utcnow().isoformat(),
        "notes": notes,
    }

    async with httpx.AsyncClient() as client:
        try:
            # In production: use actual contract service endpoint
            # response = await client.put(
            #     f"{CONTRACT_SERVICE_URL}/contracts/{contract_id}/phase",
            #     json=update_payload,
            #     headers={"Authorization": f"Bearer {actor_info.token}"},
            #     timeout=10.0,
            # )
            # response.raise_for_status()
            # result = response.json()

            # Simulated successful response
            result = {
                "contract_id": contract_id,
                "previous_phase": current_phase,
                "new_phase": new_phase.value,
                "updated_at": datetime.utcnow().isoformat(),
                "updated_by": actor_info.subject,
            }

            return result
        except httpx.HTTPError as e:
            raise Exception(f"Failed to update contract: {e}")


# ============================================================================
# MCP Tool: UpdateContractPhase
# ============================================================================


@mcp.tool()
async def update_contract_phase(
    contract_id: str = Field(description="Contract identifier (e.g., CTR-20260024)"),
    new_phase: str = Field(
        description="Target phase: draft, review, approved, executed, completed, or archived"
    ),
    reason: str = Field(description="Business reason for the phase change"),
    actor_token: str = Field(
        description="Bearer token of the user making this change (format: 'Bearer <token>')"
    ),
    obo_token: Optional[str] = Field(
        default=None,
        description="Optional bearer token if acting on behalf of another party",
    ),
    additional_notes: Optional[str] = Field(
        default=None, description="Additional context or notes"
    ),
) -> str:
    """
    Update the phase of a contract with comprehensive security and compliance checks.

    This tool handles:
    - Token validation and expiration verification
    - On-Behalf-Of (OBO) token exchange for delegated access
    - Data Loss Prevention (DLP) content scanning
    - Audit logging of all changes
    - Graceful error handling with clear messages

    Returns:
        JSON result with updated contract details or error information.
    """

    audit_metadata = {"contract_id": contract_id}

    try:
        # ====================================================================
        # 1. VALIDATE REQUEST PARAMETERS
        # ====================================================================
        try:
            validated_request = UpdateContractPhaseRequest(
                contract_id=contract_id,
                new_phase=new_phase,
                reason=reason,
                actor_token=actor_token,
                obo_token=obo_token,
                additional_notes=additional_notes,
            )
        except ValueError as e:
            log_audit_event(
                event_type="PARAMETER_VALIDATION_FAILED",
                contract_id=contract_id,
                actor_info=TokenInfo(
                    token="unknown",
                    subject="unauthenticated",
                    issued_at=datetime.utcnow(),
                    expires_at=datetime.utcnow(),
                    scopes=[],
                ),
                action="validate_request_parameters",
                result="BLOCKED",
                metadata={"error": str(e)},
            )
            return json.dumps(
                {
                    "status": "error",
                    "code": "INVALID_PARAMETERS",
                    "message": f"Request validation failed: {e}",
                }
            )

        # ====================================================================
        # 2. VALIDATE PRIMARY TOKEN
        # ====================================================================
        try:
            actor_info = validate_token(validated_request.actor_token)
            logger.info(
                f"Actor token validated for user: {actor_info.subject},"
                f" scopes: {actor_info.scopes}"
            )
        except ValueError as e:
            log_audit_event(
                event_type="TOKEN_VALIDATION_FAILED",
                contract_id=contract_id,
                actor_info=TokenInfo(
                    token="invalid",
                    subject="unknown",
                    issued_at=datetime.utcnow(),
                    expires_at=datetime.utcnow(),
                    scopes=[],
                ),
                action="validate_actor_token",
                result="BLOCKED",
                metadata={"error": str(e)},
            )
            return json.dumps(
                {
                    "status": "error",
                    "code": "INVALID_TOKEN",
                    "message": f"Token validation failed: {e}",
                }
            )

        # ====================================================================
        # 3. HANDLE OBO TOKEN EXCHANGE IF PROVIDED
        # ====================================================================
        if validated_request.obo_token:
            try:
                actor_info = exchange_obo_token(
                    validated_request.actor_token,
                    validated_request.obo_token,
                    actor_info,
                )
                logger.info(
                    f"OBO token exchange successful. Delegation chain: "
                    f"{actor_info.obo_chain}"
                )
                audit_metadata["delegation_chain"] = actor_info.obo_chain
            except ValueError as e:
                log_audit_event(
                    event_type="OBO_EXCHANGE_FAILED",
                    contract_id=contract_id,
                    actor_info=actor_info,
                    action="exchange_obo_token",
                    result="BLOCKED",
                    metadata={"error": str(e)},
                )
                return json.dumps(
                    {
                        "status": "error",
                        "code": "OBO_EXCHANGE_FAILED",
                        "message": f"On-behalf-of exchange failed: {e}",
                    }
                )

        # ====================================================================
        # 4. DLP CONTENT CHECK
        # ====================================================================
        dlp_check_reason = check_dlp_content(validated_request.reason)
        if not dlp_check_reason.passed:
            log_audit_event(
                event_type="DLP_VIOLATION_DETECTED",
                contract_id=contract_id,
                actor_info=actor_info,
                action="check_dlp_reason",
                result="BLOCKED",
                metadata={
                    "violations": dlp_check_reason.violations,
                    "field": "reason",
                },
            )
            return json.dumps(
                {
                    "status": "error",
                    "code": "DLP_VIOLATION",
                    "message": "Content contains sensitive data patterns and cannot be processed.",
                    "violations": dlp_check_reason.violations,
                }
            )

        # Check additional notes if provided
        if validated_request.additional_notes:
            dlp_check_notes = check_dlp_content(
                validated_request.additional_notes
            )
            if not dlp_check_notes.passed:
                log_audit_event(
                    event_type="DLP_VIOLATION_DETECTED",
                    contract_id=contract_id,
                    actor_info=actor_info,
                    action="check_dlp_notes",
                    result="BLOCKED",
                    metadata={
                        "violations": dlp_check_notes.violations,
                        "field": "additional_notes",
                    },
                )
                return json.dumps(
                    {
                        "status": "error",
                        "code": "DLP_VIOLATION",
                        "message": "Additional notes contain sensitive data patterns.",
                        "violations": dlp_check_notes.violations,
                    }
                )

        # ====================================================================
        # 5. EXECUTE CONTRACT UPDATE
        # ====================================================================
        result = await update_contract_phase_internal(
            contract_id=validated_request.contract_id,
            new_phase=validated_request.new_phase,
            reason=validated_request.reason,
            actor_info=actor_info,
            notes=validated_request.additional_notes,
        )

        # ====================================================================
        # 6. LOG SUCCESSFUL AUDIT EVENT
        # ====================================================================
        log_audit_event(
            event_type="CONTRACT_PHASE_UPDATED",
            contract_id=contract_id,
            actor_info=actor_info,
            action="update_contract_phase",
            result="SUCCESS",
            metadata={
                **audit_metadata,
                "new_phase": validated_request.new_phase.value,
                "reason_hash": hashlib.sha256(
                    validated_request.reason.encode()
                ).hexdigest()[:16],  # Include hash for deduplication
            },
        )

        return json.dumps(
            {"status": "success", "data": result},
            default=str,
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(f"Unexpected error in update_contract_phase: {e}")
        log_audit_event(
            event_type="INTERNAL_ERROR",
            contract_id=contract_id,
            actor_info=TokenInfo(
                token="unknown",
                subject=actor_info.subject if "actor_info" in locals() else "unknown",
                issued_at=datetime.utcnow(),
                expires_at=datetime.utcnow(),
                scopes=[],
            ),
            action="update_contract_phase",
            result="FAILURE",
            metadata={"error_type": type(e).__name__},
        )
        return json.dumps(
            {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please contact support.",
            }
        )


# ============================================================================
# Server Lifecycle
# ============================================================================


if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize server with stdio transport (for CLI usage)
        async with mcp.run_stdio():
            logger.info("UpdateContractPhase MCP server started")
            await asyncio.sleep(float("inf"))  # Keep server running

    asyncio.run(main())
