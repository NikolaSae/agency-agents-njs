# Knowledge Model

This document defines the Copilot Studio Dream Team knowledge model, including taxonomy, content types, metadata standards, and RAG integration practices.

## Knowledge Model Purpose

To provide a structured, governable content foundation that supports reliable hybrid RAG retrieval and clear agent behavior.

## Knowledge Domains

Define domain labels in the SharePoint term store and use them consistently across:
- `BusinessUnit`
- `KnowledgeDomain`
- RAG filter configuration
- prompt templates

Example domains:
- `mCommerce`
- `mParking`
- `ContractManagement`
- `RegulatoryCompliance`
- `ServiceDelivery`
- `PartnerPrograms`

## Content Types and Usage

### `AgentKnowledgeItem`

Use for any RAG source that can be referenced by an agent. This is the default content type for knowledge ingestion.

Best practices:
- include a concise summary field
- apply `RAGPriority` based on production relevance
- require `EffectiveDate` and `ApprovedBy`

### `PolicyDocument`

Use for enterprise policy and compliance content. These items are subject to higher review rigor.

Best practices:
- set `ReviewCycle`
- attach `PolicyOwner`
- enforce `SensitivityLabel`
- store policies in `GovernanceArtifacts` when they are governance artifacts rather than RAG sources

### `AgentBlueprint`

Use for agent design records, prompt templates, and workflow definitions.

Best practices:
- associate each blueprint with `ResponsibleAgent`
- version the blueprint in the title or metadata
- keep design notes and evaluation metrics linked

### `ComplianceArtifact`

Use to document audits, assessments, and compliance evidence. This content type is useful for post-incident reviews and policy records.

Best practices:
- preserve audit trails in `GovernanceArtifacts/AuditReports`
- include `ComplianceStandard` and `ReviewDate`
- keep attachments of evidence and remediation notes

### `OperationalRunbook`

Use for procedures and operator instructions. These should be easy to reference and update.

Best practices:
- include `RunbookOwner`
- attach `LastTested`
- use simple, repeatable language

## Metadata Standards

### Required metadata fields

- `BusinessUnit`
- `KnowledgeDomain`
- `ContentType`
- `SensitivityLabel`
- `RetentionLabel`
- `RAGPriority`
- `EffectiveDate`
- `ApprovedBy`

These fields ensure every item is eligible for safe production retrieval and compliance controls.

### Metadata values

Use strict, curated choices for:
- `BusinessUnit`
- `ContentType`
- `SensitivityLabel`
- `RetentionLabel`
- `RAGPriority`

Use managed metadata for `KnowledgeDomain`.

### Content item lifecycle

Each knowledge item should flow through the following lifecycle stages:

1. Draft
2. Review
3. Approved
4. Indexed
5. Active
6. Retired

Use a `LifecycleStage` metadata field on `AgentBlueprint` and `AgentAssets` at a minimum.

## RAG Integration

### Ingestion metadata payload

When indexing a document into the vector store, preserve these fields:
- `SourceURI`
- `BusinessUnit`
- `KnowledgeDomain`
- `SensitivityLabel`
- `RAGPriority`
- `EffectiveDate`
- `RetentionLabel`
- `ApprovedBy`

### Retrieval filters

Always apply these filters at query time:
- `SensitivityLabel <= user clearance`
- `BusinessUnit` and `KnowledgeDomain` align with intent
- `EffectiveDate` freshness constraints when needed
- `RAGPriority` for high-importance content

### Source reranking

Use metadata signals to rerank results:
- `RAGPriority` first
- `ApprovalStatus`
- `EffectiveDate`
- `SourceSystem`

### Handling missing metadata

If content is missing critical metadata:
- exclude it from production RAG indexes
- flag it for metadata remediation
- escalate to `KnowledgeArchitect`

## Knowledge Quality Controls

### Review gating

- New content items must be reviewed before indexing.
- `RAGPriority=High` content must be approved by a business owner.
- `Confidential` and `Highly Confidential` content must be tagged, reviewed, and only included in scope-approved indexes.

### Metadata hygiene

- Audit metadata completeness weekly.
- Enforce required fields on the SharePoint form.
- Use PowerShell sync scripts to detect missing or inconsistent values.

### Termstore governance

- Add new terms only through a documented change request.
- Keep the term set small and business-focused.
- Retire outdated terms and update content items accordingly.

## Knowledge Model Governance

- Store model governance policies in `GovernanceArtifacts/Policies`.
- Use `MasterLead` routing rules to enforce metadata and label usage.
- Track knowledge drift with Work IQ metrics.
- Maintain a `Knowledge Quality Agent` in the registry for metadata audits and remediation recommendations.
