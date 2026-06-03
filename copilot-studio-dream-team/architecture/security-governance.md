# Security, Governance & Compliance

This document defines the production security and governance model for Copilot Studio Dream Team. It is intended for enterprise platform owners, security architects, and compliance teams.

## Security Goals

- Protect sensitive content in SharePoint and RAG pipelines.
- Enforce least privilege for agent identities and tools.
- Ensure every high-risk response is reviewed and logged.
- Make classification, approval, and audit reproducible.

## Identity & Access Control

### Entra ID Agent Identities

- Each production agent should have a dedicated managed identity or service principal.
- The `MasterLead` identity has metadata read access and route decision capabilities.
- Content access for `RAGSpecialist` and domain agents must be limited by metadata scope and sensitivity.
- `SecurityAuditor` identities require elevated review privileges but may not generate final user responses.

### Conditional Access

- Require multifactor authentication for access to the Copilot Studio administration plane.
- Restrict access to Copilot Studio tools and agent backends from approved networks only.
- Use session controls for high-risk admin accounts interacting with governance tools.

## Classification & Labeling

### Purview Sensitivity Labels

Define the following labels and apply them consistently in SharePoint and Copilot Studio:

- `Public` — allowable for general internal queries and non-sensitive external communication.
- `Internal` — enterprise-use only content.
- `Confidential` — requires review before any user-facing response.
- `Highly Confidential` — blocked from automated responses unless manual escalation exists.

### Label Enforcement

- Apply labels at upload time for all `AgentKnowledge` and `GovernanceArtifacts` content.
- Use required metadata fields to prevent unlabeled content from being searchable by agents.
- Build Purview policy scanners to detect content without a valid sensitivity label.

### DLP Policies

Establish DLP rules on `AgentKnowledge` and `ExternalFeeds` for:
- financial account numbers
- personally identifiable information (PII)
- contract identifiers
- partner-protected data
- regulated identifiers.

### Inspection & Remediation

- Automate weekly scans for documents that violate DLP rules.
- Quarantine or archive non-compliant content until labels are corrected.
- Record remediation actions in `GovernanceArtifacts/AuditReports`.

## Agent Tool Governance

### Allowed / Denied Tool Matrix

| Agent | Allowed Tools | Denied Tools |
|---|---|---|
| `MasterLead` | routing, metadata queries, evaluation hooks | content editing of `Highly Confidential` |
| `RAGSpecialist` | vector search, metadata filters, SharePoint read | broad external writes |
| `KnowledgeArchitect` | content type and taxonomy APIs | direct user-facing output |
| `OrchestrationEngineer` | workflow and agent messaging | bypass approval workflows |
| `SecurityAuditor` | Purview API, DLP scanner, audit log access | user-facing generation without approval |
| `WorkIQAnalyst` | metrics and evaluation APIs | content modification |

### Governance Controls

- Require explicit approval tokens for any tool action that accesses `Confidential` or higher.
- Use the `MasterLead` to mediate all tool and agent handoffs.
- Log every tool access request and response in the audit trail.

## Compliance Checkpoints

### Agent Onboarding

For every new agent:
- document business purpose and scope
- define allowed tools and identity binding
- set evaluation threshold and review process
- register the agent in the `GovernanceArtifacts/AgentRegistry`

### Content Ingestion

For every new knowledge source:
- assign `BusinessUnit`, `KnowledgeDomain`, `ContentType`, and `SensitivityLabel`
- require a `FirstReview` before RAG indexing
- store a record in `GovernanceArtifacts/Policies`

### Response Approval

- `Confidential` responses require `SecurityAuditor` approval prior to delivery.
- `Highly Confidential` responses require manual escalation and explicit business justification.
- Keep approval records in `GovernanceArtifacts/AuditReports`.

## Audit & Monitoring

### Work IQ Monitoring

Track these indicators:
- low-confidence responses (< 80%)
- high-frequency sensitive queries
- agent route changes
- evaluation score degradation

### Audit Trail Requirements

Log the following for every user request:
- request ID and timestamp
- user identity and group membership
- selected agent route
- metadata filters applied
- sources consulted
- sensitivity label decision
- evaluation outcome
- final delivery status

### Incident Response

If a risk event occurs:
- isolate affected content source
- suspend affected agents if necessary
- run a root cause analysis
- record the incident in `GovernanceArtifacts/AuditReports`
- update the metadata policy if the root cause was taxonomy or labeling failure

## Governance Ownership

- `Platform Security Team` — controls agent identities, conditional access, and Purview policies.
- `Knowledge Governance Team` — owns metadata taxonomy, content model, and SharePoint architecture.
- `AI Operations Team` — owns agent registry, Master Lead prompt, and evaluation thresholds.
- `Audit & Compliance Team` — owns policy enforcement, DLP review, and incident documentation.
