# Master Lead Routing Rules

This document defines the routing logic for the Master Lead agent in Copilot Studio. It ensures deterministic, safe, and metadata-driven agent selection.

## Routing Principles

- Use metadata and intent classification first.
- Choose the smallest set of agents needed for the request.
- Avoid broad, unstructured routing decisions.
- Escalate sensitive requests to `SecurityAuditor`.
- Always require evaluation for production responses.

## Core Routing Patterns

### Pattern: Knowledge Lookup

- Trigger: user asks for a fact, procedure, or policy reference.
- Route to:
  - `RAGSpecialist`
  - `KnowledgeArchitect` if metadata needs refinement
- Metadata filter:
  - `BusinessUnit`
  - `KnowledgeDomain`
  - `ContentType`
  - `SensitivityLabel`

### Pattern: Business Process Request

- Trigger: user asks how to execute a process or make a decision.
- Route to:
  - `EnterpriseDomainAgent`
  - `RAGSpecialist`
- Add `SecurityAuditor` if the content is `Confidential`.

### Pattern: Governance or Policy Question

- Trigger: user asks about policy, compliance, or security controls.
- Route to:
  - `SecurityAuditor`
  - `KnowledgeArchitect` for taxonomy context
- Metadata filter: `ContentType=Policy`

### Pattern: Agent Lifecycle Management

- Trigger: request to build, update, or retire an agent.
- Route to:
  - `OrchestrationEngineer`
  - `KnowledgeArchitect`
- Use `AgentRegistry` to validate agent permissions and lifecycle state.

### Pattern: Security / Compliance Inquiry

- Trigger: request is clearly about data sensitivity, DLP, or regulations.
- Route to:
  - `SecurityAuditor`
  - `WorkIQAnalyst` if evaluation or metrics are required

## Routing Rule Examples

### Example 1: Policy search

**User request:** “Find the latest contractual approval process for partner discounts.”

**Route:**
- `RAGSpecialist`
- `KnowledgeArchitect`

**Reason:** advanced metadata-based retrieval and taxonomy alignment.

### Example 2: External sharing question

**User request:** “Can we share this customer file externally?”

**Route:**
- `SecurityAuditor`

**Reason:** sensitivity verification and DLP compliance.

### Example 3: New domain agent creation

**User request:** “Build a mCommerce financial services agent.”

**Route:**
- `EnterpriseDomainAgent`
- `SharePointMetadataArchitect`

**Reason:** business domain implementation plus content taxonomy design.

## Sensitivity Escalation Rules

- If `SensitivityLabel` is `Confidential`, include `SecurityAuditor`.
- If `SensitivityLabel` is `Highly Confidential`, block automated response and require manual escalation.
- If metadata is missing or incomplete, route to `KnowledgeArchitect` and pause production response.

## Evaluation Rules

- Every route must set `evaluationRequired` to `yes`.
- If the selected agent is `EnterpriseDomainAgent`, require `WorkIQAnalyst` scoring.
- If the response touches policy or security, require both evaluation and audit documentation.

## Fallback and Error Handling

- If no valid route exists:
  - `route`: `OrchestrationEngineer`
  - `reason`: `Request could not be matched to a production route.`
  - `nextAction`: `Escalate to human review and update routing logic.`

- If the request appears to be out of scope:
  - `route`: `Unknown`
  - `reason`: `Out of scope for current Copilot Studio deployment.`
  - `nextAction`: `Advise the user to submit a support ticket or consult the knowledge governance team.`
