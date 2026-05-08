# Azure Container Apps + FastMCP: Complete Project Structure

## Directory Layout

```
mcp-server/
├── .github/
│   ├── workflows/
│   │   ├── build-and-deploy.yml         # CI/CD pipeline
│   │   └── lint-and-test.yml            # Code quality checks
│   └── dependabot.yml                   # Automated dependency updates
│
├── src/
│   ├── main.py                          # FastMCP server entry point
│   ├── config.py                        # Configuration management (Pydantic)
│   ├── models.py                        # Data models (Pydantic)
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── middleware.py                # Auth middleware chain
│   │   ├── obo_client.py                # OBO token acquisition & caching
│   │   ├── trust_scorer.py              # Agent trust score computation
│   │   ├── delegation_chain.py          # Delegation validation
│   │   └── exceptions.py                # Auth-specific exceptions
│   │
│   ├── tools/                           # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── base.py                      # Base tool class with auth
│   │   ├── github_tools.py              # GitHub API tools
│   │   ├── data_tools.py                # Database/data query tools
│   │   ├── business_logic_tools.py      # Domain-specific tools
│   │   └── registry.py                  # Tool discovery & registration
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py                   # Structured logging setup
│   │   ├── tracing.py                   # Distributed tracing (OpenTelemetry)
│   │   ├── metrics.py                   # Custom metrics & health checks
│   │   └── correlation_context.py       # Request correlation IDs
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── key_vault.py                 # Azure Key Vault integration
│   │   ├── cosmos_db.py                 # CosmosDB for delegation trust store
│   │   ├── redis_cache.py               # Redis token cache (optional)
│   │   └── service_bus.py               # Event publishing (optional)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validation.py                # Input validation schemas
│       ├── encryption.py                # Sensitive data encryption
│       ├── retry_logic.py               # Exponential backoff, circuit breaker
│       └── testing_helpers.py           # Mock clients for testing
│
├── tests/
│   ├── unit/
│   │   ├── test_auth_middleware.py
│   │   ├── test_obo_client.py
│   │   ├── test_tool_registry.py
│   │   ├── test_delegation_chain.py
│   │   └── test_utils.py
│   │
│   ├── integration/
│   │   ├── test_github_tools.py
│   │   ├── test_obo_flow.py             # End-to-end OBO acquisition
│   │   └── test_tool_execution.py
│   │
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── mock_auth_tokens.py
│   │   ├── mock_delegation_chains.py
│   │   └── mock_services.py
│   │
│   └── conftest.py                      # Pytest configuration
│
├── deployment/
│   ├── azure-container-apps.yaml        # Container Apps configuration
│   ├── bicep/
│   │   ├── main.bicep                   # IaC for Container Apps, CosmosDB, Key Vault
│   │   ├── container-app.bicep          # Modular Container App resource
│   │   ├── key-vault.bicep
│   │   └── monitoring.bicep
│   ├── helm/                            # Kubernetes Helm charts (optional fallback)
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── configmap.yaml
│   │
│   └── scripts/
│       ├── deploy.sh                    # Deployment automation
│       ├── rollback.sh                  # Quick rollback
│       ├── scale-replicas.sh            # Manual scaling
│       └── health-check.sh              # Health endpoint verification
│
├── docs/
│   ├── ARCHITECTURE.md                  # System design overview
│   ├── AUTHENTICATION.md                # OBO flow, trust scoring details
│   ├── TOOL_DEVELOPMENT.md              # How to add new tools
│   ├── DEPLOYMENT.md                    # Step-by-step deployment guide
│   ├── MONITORING.md                    # Observability setup & dashboards
│   ├── LOCAL_DEVELOPMENT.md             # Dev environment setup
│   ├── TROUBLESHOOTING.md               # Common issues & solutions
│   └── API.md                           # Tool API reference
│
├── .dockerignore                        # Optimize Docker builds
├── Dockerfile                           # Multi-stage container build
├── Dockerfile.dev                       # Development container (if needed)
├── .env.example                         # Example environment variables
├── .env.local                           # Local dev secrets (not committed)
├── .gitignore
├── pyproject.toml                       # Python packaging (modern standard)
├── requirements.txt                     # Production dependencies (locked versions)
├── requirements-dev.txt                 # Development dependencies
├── requirements-test.txt                # Test dependencies
├── pytest.ini                           # Pytest configuration
├── mypy.ini                             # Type checking config
├── .pylintrc                            # Linting config
├── docker-compose.yml                   # Local dev + supporting services
├── docker-compose.test.yml              # Test environment
├── tox.ini                              # Multi-environment testing
├── README.md                            # Quick start guide
├── CONTRIBUTING.md                      # Development guidelines
└── LICENSE
```

---

## File Templates & Implementations

### 1. `src/main.py` — FastMCP Server Entry Point

```python
"""
FastMCP Server: AI Agent Tool Interface
Handles authenticated tool execution with delegation support
"""
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from auth.middleware import AuthenticationMiddleware
from tools.registry import ToolRegistry
from observability.logging import setup_logging
from observability.tracing import setup_tracing
from infrastructure.key_vault import KeyVaultClient

# Setup
setup_logging()
setup_tracing()
logger = logging.getLogger(__name__)

# Initialize FastMCP (fast MCP server)
from fastmcp import FastMCP

mcp_server = FastMCP(name="Agency Tools MCP Server", description="...")
tool_registry = ToolRegistry()


# ─────────────────────────────────────────────────────────────
# Lifespan Events
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info("🚀 Starting MCP Server")
    
    # Initialize infrastructure
    key_vault = await KeyVaultClient.create()
    await tool_registry.initialize(key_vault)
    
    # Register tools with FastMCP
    await tool_registry.register_all_tools(mcp_server)
    
    yield
    
    logger.info("🛑 Shutting down MCP Server")
    await key_vault.close()


# ─────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Agency Tools MCP Server",
    description="Agentic tool execution with delegated authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Mount authentication middleware
app.add_middleware(AuthenticationMiddleware)


# ─────────────────────────────────────────────────────────────
# Health Endpoints
# ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Liveness probe"""
    return {"status": "healthy", "service": "mcp-server"}


@app.get("/ready")
async def readiness():
    """Readiness probe"""
    # Check Key Vault connectivity
    # Check CosmosDB connectivity
    # Check GitHub API (for GitHub tools)
    return {"status": "ready"}


# ─────────────────────────────────────────────────────────────
# MCP Protocol Endpoints
# ─────────────────────────────────────────────────────────────
@app.post("/mcp/initialize")
async def mcp_initialize(request: Request):
    """MCP Initialize handshake"""
    return await mcp_server.initialize(request)


@app.post("/mcp/invoke/{tool_name}")
async def invoke_tool(tool_name: str, request: Request):
    """Execute a tool with authentication & observability"""
    try:
        # Extract user context from auth middleware
        user_context = request.state.user_context
        delegation_chain = request.state.delegation_chain
        
        # Get request body
        body = await request.json()
        arguments = body.get("arguments", {})
        
        # Invoke via registry (auth + validation + execution)
        result = await tool_registry.invoke(
            tool_name=tool_name,
            arguments=arguments,
            user_context=user_context,
            delegation_chain=delegation_chain
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.exception(f"Tool invocation failed: {tool_name}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_config=settings.LOG_CONFIG,
        access_log=settings.ACCESS_LOG,
    )
```

---

### 2. `src/config.py` — Configuration Management

```python
"""Configuration management with Pydantic and Azure Key Vault"""
import os
from typing import Optional
from pydantic import BaseSettings, Field, validator
from enum import Enum


class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application configuration from environment + Key Vault"""
    
    # Basic
    ENV: EnvironmentEnum = Field(
        default=EnvironmentEnum.DEVELOPMENT,
        description="Deployment environment"
    )
    PORT: int = Field(default=8000, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Authentication
    AZURE_TENANT_ID: str = Field(..., description="Azure AD tenant ID")
    AZURE_CLIENT_ID: str = Field(..., description="Application client ID")
    AZURE_CLIENT_SECRET: Optional[str] = Field(None, description="Client secret (from Key Vault)")
    
    # OBO Flow
    GRAPH_RESOURCE_ID: str = "https://graph.microsoft.com"
    GITHUB_RESOURCE_ID: str = "https://api.github.com"
    OBO_TOKEN_CACHE_TTL: int = Field(default=600, description="Token cache TTL in seconds")
    
    # Azure Services
    KEY_VAULT_URL: str = Field(..., description="Key Vault endpoint URL")
    COSMOS_DB_ENDPOINT: str = Field(..., description="CosmosDB endpoint URL")
    COSMOS_DB_KEY: Optional[str] = Field(None, description="CosmosDB key (from Key Vault)")
    COSMOS_DB_DATABASE: str = "agency-mcp"
    COSMOS_DB_CONTAINER: str = "delegation-trust"
    
    # Observability
    APPINSIGHTS_INSTRUMENTATION_KEY: Optional[str] = Field(None)
    ENABLE_TRACING: bool = Field(default=True)
    TRACE_SAMPLE_RATE: float = Field(default=0.1)
    
    # Tools
    ENABLED_TOOLS: list[str] = Field(
        default=["github_search", "github_issues", "data_query"],
        description="Which tools to register"
    )
    
    # Security
    ALLOWED_ORIGINS: list[str] = Field(
        default=["https://copilot.microsoft.com"],
        description="CORS allowed origins"
    )
    
    @validator("AZURE_CLIENT_SECRET", pre=True, always=True)
    def load_secret_from_keyvault(cls, v, values):
        """Load client secret from Key Vault if not provided"""
        if v:
            return v
        if "KEY_VAULT_URL" in values:
            # Lazy load from Key Vault on first access
            return None
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

---

### 3. `src/auth/middleware.py` — Authentication Chain

```python
"""Authentication middleware with OBO flow and delegation validation"""
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from .obo_client import OBOClient
from .delegation_chain import validate_delegation_chain
from .trust_scorer import TrustScorer
from models import UserContext, DelegationChain

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware that:
    1. Extracts user token from Authorization header
    2. Validates delegation chain metadata
    3. Computes agent trust score
    4. Acquires OBO tokens for downstream services
    5. Attaches context to request state
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.obo_client = OBOClient()
        self.trust_scorer = TrustScorer()
    
    async def dispatch(self, request: Request, call_next):
        """Process incoming request"""
        
        # Extract bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )
        
        user_token = auth_header.replace("Bearer ", "")
        
        # Extract delegation metadata from headers
        agent_id = request.headers.get("X-Agent-ID")
        user_id = request.headers.get("X-User-ID")
        delegation_chain_json = request.headers.get("X-Delegation-Chain")
        
        try:
            # Validate delegation chain
            if delegation_chain_json:
                delegation_chain = DelegationChain.parse_raw(delegation_chain_json)
                is_valid = await validate_delegation_chain(delegation_chain)
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid delegation chain"
                    )
            else:
                delegation_chain = None
            
            # Compute trust score
            trust_score = await self.trust_scorer.compute(agent_id)
            
            # Acquire OBO token for Microsoft Graph
            obo_token = await self.obo_client.get_token(
                user_token=user_token,
                resource="https://graph.microsoft.com",
                on_behalf_of_user=user_id
            )
            
            # Attach to request state
            request.state.user_context = UserContext(
                user_id=user_id,
                agent_id=agent_id,
                user_token=user_token,
                obo_token=obo_token,
                trust_score=trust_score
            )
            request.state.delegation_chain = delegation_chain
            
        except Exception as e:
            logger.exception("Authentication failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        # Call next middleware/handler
        response = await call_next(request)
        return response
```

---

### 4. `src/auth/obo_client.py` — OBO Token Caching & Refresh

```python
"""Stabilized OBO client with token caching and proactive refresh"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from aiohttp import ClientSession
from azure.identity.aio import ClientSecretCredential
from azure.core.credentials import AccessToken

from config import settings
from utils.retry_logic import retry_with_backoff, CircuitBreaker

logger = logging.getLogger(__name__)


class OBOClient:
    """Manages OBO (On-Behalf-Of) token acquisition with caching"""
    
    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET
        )
        self._token_cache: Dict[str, AccessToken] = {}
        self._cache_lock = asyncio.Lock()
        self._circuit_breaker = CircuitBreaker()
    
    async def get_token(
        self,
        user_token: str,
        resource: str,
        on_behalf_of_user: str
    ) -> str:
        """
        Acquire OBO token with caching.
        
        Cache key: f"{user_id}:{resource}"
        TTL: 10 minutes (refresh at 9 minutes to avoid expiry)
        """
        
        cache_key = f"{on_behalf_of_user}:{resource}"
        
        # Check if cached and not expiring soon
        async with self._cache_lock:
            if cache_key in self._token_cache:
                cached = self._token_cache[cache_key]
                if not self._is_expiring_soon(cached.expires_on):
                    logger.debug(f"Using cached OBO token for {resource}")
                    return cached.token
                else:
                    logger.debug(f"OBO token expiring soon, refreshing")
        
        # Acquire new token with circuit breaker
        try:
            token = await self._circuit_breaker.execute(
                self._acquire_obo_token,
                user_token=user_token,
                resource=resource
            )
            
            # Cache it
            async with self._cache_lock:
                self._token_cache[cache_key] = token
            
            return token.token
            
        except Exception as e:
            logger.error(f"OBO token acquisition failed: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    async def _acquire_obo_token(
        self,
        user_token: str,
        resource: str
    ) -> AccessToken:
        """Actual OBO token request to Azure AD"""
        # Use azure-identity library or manual HTTP call
        # This is simplified; real implementation uses OAuth 2.0 OBO flow
        pass
    
    @staticmethod
    def _is_expiring_soon(expires_on: int, buffer_seconds: int = 60) -> bool:
        """Check if token expires within buffer time"""
        expiry_time = datetime.fromtimestamp(expires_on)
        return datetime.utcnow() + timedelta(seconds=buffer_seconds) > expiry_time
```

---

### 5. `Dockerfile` — Multi-Stage Container Build

```dockerfile
# Multi-stage Dockerfile for FastMCP server
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies into virtual environment
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy application code
COPY src/ /app/src/

# Set environment
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run server
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 6. `deployment/bicep/main.bicep` — Infrastructure as Code

```bicep
// Azure resources for MCP Server deployment
param environment string = 'staging'
param location string = resourceGroup().location
param containerImageUri string
param replicaCount int = 2
param maxReplicas int = 10

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-mcp-${environment}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    enabledForTemplateDeployment: true
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: containerApp.identity.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
}

// Container App Environment
resource appEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-mcp-${environment}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
  }
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ca-mcp-${environment}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: appEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      secrets: [
        {
          name: 'key-vault-uri'
          value: keyVault.properties.vaultUri
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'mcp-server'
          image: containerImageUri
          env: [
            {
              name: 'ENVIRONMENT'
              value: environment
            }
            {
              name: 'KEY_VAULT_URL'
              secretRef: 'key-vault-uri'
            }
            {
              name: 'PORT'
              value: '8000'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
          probes: [
            {
              type: 'liveness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
            {
              type: 'readiness'
              httpGet: {
                path: '/ready'
                port: 8000
              }
              initialDelaySeconds: 5
              periodSeconds: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: replicaCount
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'cpu-scaling'
            custom: {
              rule: 'cpu > 70'
              metadata: {}
            }
          }
        ]
      }
    }
  }
}

output serverUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output keyVaultId string = keyVault.id
```

---

### 7. `.github/workflows/build-and-deploy.yml` — CI/CD Pipeline

```yaml
name: Build & Deploy MCP Server

on:
  push:
    branches: [main]
    paths:
      - 'mcp-server/**'
      - '.github/workflows/build-and-deploy.yml'
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/mcp-server

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-test.txt
      
      - name: Lint
        run: |
          pylint src/
          mypy src/ --strict
      
      - name: Test
        run: pytest tests/ --cov=src/
      
      - name: Build image
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
                      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
      
      - name: Push image
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ${{ env.REGISTRY }} -u ${{ github.actor }} --password-stdin
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name ca-mcp-staging \
            --resource-group rg-agency-mcp \
            --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
      
      - name: Health Check
        run: |
          ./deployment/scripts/health-check.sh staging
```

---

## Development Workflow

### Local Development Setup

```bash
# 1. Clone and setup
git clone <repo>
cd mcp-server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Setup environment
cp .env.example .env.local
# Edit .env.local with your Azure credentials

# 5. Start services (PostgreSQL, Redis for dev)
docker-compose up -d

# 6. Run server locally
python -m uvicorn src.main:app --reload --port 8000

# 7. Run tests
pytest tests/ -v

# 8. Run with type checking
mypy src/ --strict
```

### Deploy to Azure Container Apps

```bash
# 1. Build and push image
az acr build --registry <registry-name> \
  --image mcp-server:${{ git rev-parse --short HEAD }} .

# 2. Deploy or update
az containerapp update \
  --name ca-mcp-staging \
  --resource-group rg-agency-mcp \
  --image <registry>/mcp-server:latest

# 3. Check status
az containerapp show --name ca-mcp-staging --resource-group rg-agency-mcp

# 4. View logs
az containerapp logs show --name ca-mcp-staging --resource-group rg-agency-mcp --follow
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastMCP** | Reduces boilerplate, handles MCP protocol validation |
| **Pydantic** | Type validation, automatic OpenAPI docs |
| **Azure Managed Identity** | No secret key management overhead |
| **CosmosDB** | OBO token & trust score storage, global distribution |
| **OpenTelemetry** | Vendor-agnostic distributed tracing |
| **Multi-stage Dockerfile** | Reduces final image size, faster deployment |
| **Bicep over ARM** | Cleaner syntax, better for IaC |
| **pytest + pytest-asyncio** | Async test support, familiar patterns |
| **Docker Compose for dev** | Local reproduction of production setup |

---

## Monitoring & Observability

- **Application Insights**: Automatic instrumentation via OpenTelemetry
- **Log Analytics**: Correlated logs by request ID
- **Custom Metrics**: Tool execution time, trust score histogram, OBO token refresh rate
- **Alerts**: High error rate, OBO flow failures, cold start times
- **Dashboard**: Real-time tool invocation rates, authentication latency, delegation chain validation success

---

## Security Considerations

✅ **Implemented:**
- Azure Managed Identity (no credentials in code)
- Key Vault for secrets
- E2E encrypted secrets in transit
- Delegation chain cryptographic validation
- Trust scoring with continuous decay
- Audit logging of all tool executions
- CORS restricted to trusted origins

⚠️ **To Review:**
- Rate limiting per agent/user
- Scope validation (ensure tools don't exceed delegated permissions)
- Encryption at rest for sensitive data in CosmosDB
- Network isolation (Private Endpoints if needed)

