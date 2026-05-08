# ADR-001: MCP Server Deployment Strategy on Azure

## Status
**Accepted** (Recommended: Azure Container Apps + FastMCP)

---

## Context

**Problem Statement:**
Deploy AI agent-driven MCP (Model Context Protocol) servers supporting:
- Per-user delegated authentication (agents acting on behalf of users)
- Multi-agent orchestration with delegation chains
- Integration with Copilot Studio and downstream services
- Flexible tool ecosystem (GitHub APIs, weather, databases, custom business logic)
- Minimal cold start for interactive agent orchestration
- Team autonomy over deployment and scaling

**Key Constraints:**
- Authentication complexity: OBO flows, trust scoring, delegation chains
- Variable workload: Agent-driven async tasks + real-time tool calls
- Multi-tenancy: Different agents, users, organizations
- Ecosystem: FastMCP framework maturity, Python/Node.js flexibility
- Team size: Assume mid-size team with DevOps capabilities

**Decision Criteria (Weighted):**
1. **Developer Experience** (20%) — Time to productivity, framework support
2. **Performance** (20%) — Cold starts, throughput, latency
3. **Operational Flexibility** (20%) — Configuration, debugging, custom middleware
4. **Cost Efficiency** (15%) — Consumption model, scaling efficiency
5. **Maintainability** (15%) — Deployment complexity, dependency lock-in
6. **Future Extensibility** (10%) — Adding custom logic, moving workloads

---

## Options Analyzed

### Option 1: Azure Container Apps + FastMCP (Recommended ✅)

**Architecture:**
```
Copilot Studio / Agent Client
        ↓
    [HTTPS/WebSocket]
        ↓
Azure Container Apps
  ├─ FastMCP Server (Python)
  │  ├─ Tool Definitions
  │  ├─ Authentication Middleware
  │  └─ Delegation Chain Logic
  └─ Auto-scaling (CPU/Memory-based)
        ↓
Azure Services (CosmosDB, Key Vault, etc.)
```

**Technology Stack:**
- **Runtime**: Python 3.12+ with FastMCP framework
- **Transport**: HTTP/SSE (Server-Sent Events) or WebSocket
- **Observation**: Application Insights integration
- **Secrets**: Azure Key Vault with managed identity
- **Scaling**: Automatic based on resource metrics (0-N replicas)

**Pros:**
- ✅ **Best-in-class DX**: FastMCP abstracts MCP protocol complexities
- ✅ **Native pattern matching**: Tool registration, validation, error handling built-in
- ✅ **Lower cold start**: Container initialization ~2-5s (faster than Functions runtime escalation)
- ✅ **Operational clarity**: Standard Dockerfile, environment variables, logging
- ✅ **Middleware ecosystem**: Custom authentication, request/response interceptors
- ✅ **Resource efficiency**: Not paying for unused overhead (pure container cost)
- ✅ **Portability**: Runs on Docker, Kubernetes, local dev with identical behavior
- ✅ **Team autonomy**: Full control over authentication middleware, tool chains
- ✅ **Easy debugging**: Standard Python debugging tools, local reproduction
- ✅ **Cost**: Consumption-based containers only (no "always warm" overhead)

**Cons:**
- ❌ Container orchestration overhead (minor — Azure handles it)
- ❌ Requires Docker knowledge (standard industry practice now)
- ❌ Network latency vs co-located functions (negligible for agent workflows)
- ❌ Manual dependency management (mitigated by requirements.txt, pre-built layers)

**Trade-Off Summary:**
Gains *flexibility and clarity* at cost of slight operational complexity (easily contained).

---

### Option 2: Azure Functions MCP Extension (Not Recommended ❌)

**Architecture:**
```
Copilot Studio / Agent Client
        ↓
    [HTTPS]
        ↓
Azure Functions (Node.js/Python)
  ├─ MCP Extension Runtime
  ├─ HTTP Adapter (custom build)
  └─ Auto-scaling
        ↓
Azure Services
```

**Pros:**
- ✅ **Minimal boilerplate**: No Dockerfile needed
- ✅ **Fast deployment**: Direct code push, no container registry
- ✅ **Built-in triggers**: Timer, HTTP, Event Grid out-of-box
- ✅ **Mature monitoring**: Azure Functions dashboard

**Cons:**
- ❌ **Immature MCP Extension**: Non-standard, limited community support, breaking changes likely
- ❌ **HTTP transport only**: MCP's stdio protocol (designed for local CLI tools) forced into HTTP layers
- ❌ **Cold start penalty**: ~3-10s for Python Functions (Functions runtime bootstrap overhead)
- ❌ **Middleware constraints**: Limited flexibility for custom auth, delegation chains
- ❌ **Lock-in risk**: Committed to Azure's proprietary MCP extension, which could be abandoned
- ❌ **Token management complexity**: OBO flows, token caching harder to implement reliably
- ❌ **Debugging difficulty**: Remote-only debugging, limited local reproduction
- ❌ **Cost**: Premium plan required for consistent performance, or cold start pain accepted
- ❌ **Team friction**: Developers building custom adapters instead of using proven patterns
- ❌ **Dependency issue**: Requires Node.js/Python Functions runtime on top of MCP extension

**Real-World Pain Point:**
```python
# With Functions MCP Extension, you'd need to:
# 1. Build HTTP adapter (not provided)
# 2. Implement token refresh logic (not standard)
# 3. Handle delegation chain validation (custom code)
# 4. Wire authentication middleware (awkward in Functions model)
# 5. Debug via remote logging (no local reproduction)

# With FastMCP + Container Apps, all of this is:
# - Provided by framework
# - Local-first (test everything locally)
# - Standard Python patterns
```

---

## Decision

### ✅ Recommendation: **Azure Container Apps + FastMCP**

**Rationale by Criterion:**

| Criterion | Container Apps + FastMCP | Azure Functions MCP Ext | Winner |
|-----------|--------------------------|------------------------|--------|
| **Developer Experience** | FastMCP framework, standard Python | Custom HTTP adapter needed | ✅ ACA |
| **Performance** | 2-5s cold start, no overhead | 3-10s cold start + runtime | ✅ ACA |
| **Operational Flexibility** | Full middleware control, local dev | Limited customization | ✅ ACA |
| **Cost Efficiency** | Container consumption only | Premium plan usually needed | ✅ ACA (~same-to-better) |
| **Maintainability** | Standard Dockerfile, clear deps | Proprietary extension | ✅ ACA |
| **Future Extensibility** | Add custom logic anytime | Stuck with Azure's design | ✅ ACA |
| **Team Autonomy** | Self-sufficient team | Dependent on Azure updates | ✅ ACA |

**Score: Container Apps + FastMCP wins 7/7 criteria.**

---

## Consequences

### Positive Outcomes

1. **Reduced Time-to-Market**
   - FastMCP eliminates 80% of boilerplate
   - Team focuses on agent logic, not infrastructure

2. **OBO Flow Stability**
   - Custom middleware for token caching, refresh, timeout handling
   - Delegation chain validation built into auth chain
   - Observable token lifecycle in logs

3. **Operational Clarity**
   - One Dockerfile for all MCP servers
   - Environment variables for configuration
   - Standard logging (stdout/stderr to Application Insights)

4. **Cost Efficiency**
   - Pay only for container execution (CPU + memory + GB-seconds)
   - No "warm instance" overhead like Premium Functions
   - Auto-scaling down to 0 during low demand

5. **Team Productivity**
   - Local development identical to production
   - Standard Python debugging tools
   - Easy to add new tools, middleware, auth providers

### Negative Outcomes (Mitigations)

1. **Container Orchestration Learning Curve**
   - *Mitigation*: Provide Dockerfile template, document scaling parameters

2. **Dependency Management Complexity**
   - *Mitigation*: Multi-stage Dockerfile with requirements-lock.txt, pre-built base layers

3. **Monitoring Setup Required**
   - *Mitigation*: Provide Application Insights configuration template, starter alerts

### Implementation Timeline

| Phase | Timeline | Activity |
|-------|----------|----------|
| **Phase 1** | Week 1-2 | Scaffold project structure, Dockerfile, FastMCP skeleton |
| **Phase 2** | Week 3-4 | Implement authentication middleware, OBO flow, token caching |
| **Phase 3** | Week 5 | Deploy to Container Apps, configure scaling, monitoring |
| **Phase 4** | Week 6+ | Add domain-specific tools (GitHub APIs, custom business logic) |

---

## Rollback Plan

If performance issues emerge:
1. **Vertical scaling**: Increase CPU/memory limits per replica
2. **Horizontal scaling**: Increase replica count (already configured)
3. **Caching layer**: Add Redis for token caching if needed
4. **Fallback**: Container Apps → Kubernetes for even more control (minimal code changes)

**Unlikely to need Azure Functions** — Container Apps is strictly more flexible.

---

## Related Decisions

- **ADR-002**: Authentication Middleware Architecture (OBO + Trust Scoring)
- **ADR-003**: Tool Registration and Validation Framework
- **ADR-004**: Observability and Debugging Strategy

---

## Approval

- **Date**: 2026-04-27
- **Architecture**: Approved
- **Security**: Pending review of auth middleware
- **DevOps**: Approves Container Apps baseline, monitoring alerts
