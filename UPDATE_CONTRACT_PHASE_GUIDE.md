"""
Configuration and deployment guide for UpdateContractPhase MCP tool.
"""

# ============================================================================
# CLIENT-SIDE MCP CONFIGURATION
# ============================================================================
# 
# Add this to your Claude/AI client's MCP server configuration:
#
# File: ~/.claude/config.json (or equivalent for your client)
# 
# {
#   "mcpServers": {
#     "contract-manager": {
#       "command": "python",
#       "args": ["-m", "update_contract_phase_mcp"],
#       "env": {
#         "ACCESS_TOKEN_LIFETIME": "3600",
#         "OBO_SCOPES": "contract:write audit:read delegation",
#         "LOG_LEVEL": "INFO"
#       }
#     }
#   }
# }


# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================
# 
# ACCESS_TOKEN_LIFETIME     (default: 3600)
#   Maximum lifetime of auth tokens in seconds
#
# OBO_SCOPES               (default: "contract:write audit:read")
#   Space-separated scopes required for on-behalf-of exchanges
#
# AUDIT_LOG_PATH           (default: "./audit.log")
#   Path where audit events are written
#
# CONTRACT_SERVICE_URL     (required in production)
#   URL of backend contract management service
#
# JWT_PUBLIC_KEY_URL       (required in production)
#   URL to fetch JWT public key for signature verification


# ============================================================================
# SECURITY PATTERNS IMPLEMENTED
# ============================================================================
#
# 1. TOKEN VALIDATION
#    ✓ Signature verification with JWT
#    ✓ Expiration time checking
#    ✓ Required scope validation
#    ✓ Bearer token format validation
#
# 2. ON-BEHALF-OF (OBO) EXCHANGE
#    ✓ Actor permission verification (requires "delegation" or "admin" scope)
#    ✓ Delegation chain tracking (who delegated to whom)
#    ✓ OBO token signature validation
#    ✓ Scope preservation through delegation
#
# 3. DLP (DATA LOSS PREVENTION)
#    ✓ Sensitive field pattern detection (SSN, credit cards, API keys, etc.)
#    ✓ Multi-field scanning (reason, notes, metadata)
#    ✓ Blocking of requests with sensitive content
#    ✓ Violation reporting for audit
#
# 4. AUDIT LOGGING
#    ✓ Structured JSON audit events
#    ✓ Complete audit trail per contract update
#    ✓ Actor + delegation chain tracking
#    ✓ Success/failure recording
#    ✓ Timestamp and metadata capture
#
# 5. ERROR HANDLING
#    ✓ Graceful failure with actionable error messages
#    ✓ No stack traces leaked to client
#    ✓ Audit logging of all errors
#    ✓ Typed error codes for programmatic handling


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

# EXAMPLE 1: Basic contract phase update with token validation
#
# Request:
# {
#   "contract_id": "CTR-20260024",
#   "new_phase": "approved",
#   "reason": "Approved by legal team per contract review process",
#   "actor_token": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
# }
#
# Expected Response (Success):
# {
#   "status": "success",
#   "data": {
#     "contract_id": "CTR-20260024",
#     "previous_phase": "review",
#     "new_phase": "approved",
#     "updated_at": "2026-04-27T14:32:00.000000",
#     "updated_by": "user-12345"
#   }
# }


# EXAMPLE 2: On-Behalf-Of (OBO) token exchange
#
# Request:
# {
#   "contract_id": "CTR-20260025",
#   "new_phase": "executed",
#   "reason": "Execution authorized by department head",
#   "actor_token": "Bearer <supervisor_token>",
#   "obo_token": "Bearer <department_head_token>",
# }
#
# Audit Log Entry:
# {
#   "timestamp": "2026-04-27T14:32:00",
#   "event_type": "CONTRACT_PHASE_UPDATED",
#   "contract_id": "CTR-20260025",
#   "actor": "supervisor-444",
#   "delegation_chain": ["department-head-555"],  # Who delegated to whom
#   "result": "SUCCESS"
# }


# EXAMPLE 3: DLP violation detection
#
# Request (with sensitive data in reason):
# {
#   "contract_id": "CTR-20260026",
#   "new_phase": "approved",
#   "reason": "Approved after SSN verification: 123-45-6789",
#   "actor_token": "Bearer ..."
# }
#
# Response (Blocked):
# {
#   "status": "error",
#   "code": "DLP_VIOLATION",
#   "message": "Content contains sensitive data patterns and cannot be processed.",
#   "violations": [
#     "Potential sensitive field reference: ssn"
#   ]
# }
#
# Audit Log Entry:
# {
#   "event_type": "DLP_VIOLATION_DETECTED",
#   "contract_id": "CTR-20260026",
#   "result": "BLOCKED",
#   "metadata": {
#     "violations": ["Potential sensitive field reference: ssn"],
#     "field": "reason"
#   }
# }


# EXAMPLE 4: Token validation failure
#
# Request (expired token):
# {
#   "contract_id": "CTR-20260027",
#   "new_phase": "draft",
#   "reason": "Reverting to draft for revision",
#   "actor_token": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # Expired
# }
#
# Response:
# {
#   "status": "error",
#   "code": "INVALID_TOKEN",
#   "message": "Token validation failed: Token has expired"
# }
#
# Audit Log Entry:
# {
#   "event_type": "TOKEN_VALIDATION_FAILED",
#   "contract_id": "CTR-20260027",
#   "result": "BLOCKED",
#   "metadata": {
#     "error": "Token has expired"
#   }
# }


# ============================================================================
# TESTING THE TOOL
# ============================================================================
#
# Unit test example:
#
# import pytest
# import asyncio
# from update_contract_phase_mcp import (
#     validate_token, TokenInfo, check_dlp_content, 
#     update_contract_phase
# )
#
#
# @pytest.mark.asyncio
# async def test_token_validation_failure():
#     """Expired token should raise ValueError."""
#     with pytest.raises(ValueError, match="expired"):
#         validate_token("Bearer expired.token.here")
#
#
# @pytest.mark.asyncio
# async def test_dlp_detection():
#     """DLP should detect sensitive patterns."""
#     result = check_dlp_content("Customer SSN: 123-45-6789")
#     assert not result.passed
#     assert "ssn" in result.flagged_fields[0].lower()
#
#
# @pytest.mark.asyncio
# async def test_obo_without_permission():
#     """OBO should fail if actor lacks delegation scope."""
#     actor_token = "Bearer limited.token"
#     obo_token = "Bearer delegate.token"
#     
#     actor_info = TokenInfo(
#         token="limited.token",
#         subject="user-1",
#         issued_at=datetime.utcnow(),
#         expires_at=datetime.utcnow() + timedelta(hours=1),
#         scopes=["contract:write"]  # Missing "delegation" scope
#     )
#     
#     with pytest.raises(ValueError, match="delegation"):
#         exchange_obo_token(actor_token, obo_token, actor_info)
#
#
# Command to run tests:
# pytest -v test_update_contract_phase.py


# ============================================================================
# AUDIT LOG FORMAT AND RETENTION
# ============================================================================
#
# Audit events are written to audit.log in JSON lines format.
# Each line is a complete audit entry:
#
# {"timestamp": "2026-04-27T14:32:00.000000", "event_type": "CONTRACT_PHASE_UPDATED", "contract_id": "CTR-20260024", "actor": "user-12345", "actor_scopes": ["contract:write", "audit:read"], "delegation_chain": [], "action": "update_contract_phase_internal", "result": "SUCCESS", "metadata": {...}}
#
# For production:
#
# 1. Configure centralized logging (CloudWatch, DataDog, ELK stack)
# 2. Set retention: 7 years for compliance (varies by jurisdiction)
# 3. Rotate logs daily
# 4. Encrypt audit logs at rest and in transit
#
# Example CloudWatch integration:
#
# import watchtower
# import logging_loki
#
# loki_handler = logging_loki.LokiHandler(
#     url="https://logs.example.com/loki/api/v1/push",
#     tags={"app": "contract-manager"},
#     auth=("user", os.environ["LOKI_PASSWORD"])
# )
# audit_logger.addHandler(loki_handler)


# ============================================================================
# PRODUCTION CHECKLIST
# ============================================================================
#
# Security:
# ☐ JWT signature verification implemented and tested
# ☐ Token expiration validation working
# ☐ HTTPS/TLS for all external API calls
# ☐ API key rotation policy established
# ☐ DLP rules reviewed by compliance team
# ☐ OBO delegation audited for scope creep
#
# Monitoring:
# ☐ Audit log aggregation configured
# ☐ Alerting on DLP violations
# ☐ Token validation failures triggering security reviews
# ☐ Error rates tracked and alarmed
#
# Operations:
# ☐ Load testing completed (target: <500ms per request)
# ☐ Deployment tested in staging environment
# ☐ Rollback procedure documented
# ☐ On-call runbook created for common failures
# ☐ Audit log retention policy implemented
#
# Compliance:
# ☐ Data handling documented (what's logged, where, how long)
# ☐ Legal review of audit requirements
# ☐ SOC 2 audit scope defined
# ☐ Data minimization: only necessary fields in audit logs
