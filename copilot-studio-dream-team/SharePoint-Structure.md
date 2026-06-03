# SharePoint Structure for Copilot Studio Dream Team

This document describes the SharePoint site collection, libraries, content types, metadata columns, and recommended views for the Copilot Studio enterprise implementation.

## Site Collection

- Site collection name: `CopilotStudio`
- Primary purpose: centralized knowledge store, governance artifacts, agent assets, and regulated external feeds used by Copilot Studio and its RAG pipelines.

## Site Libraries

### `AgentKnowledge`

Purpose: authoritative knowledge repository for RAG, prompt context, and enterprise content retrieval.

Required features:
- Versioning enabled
- Content approval turned on for production documents
- DLP and sensitivity label enforcement active
- Metadata navigation enabled

Recommended subfolders:
- `Finance`
- `HR`
- `Legal`
- `Sales`
- `IT`
- `Operations`

Typical use:
- policy documents
- playbooks
- procedure manuals
- regulated reference content

### `GovernanceArtifacts`

Purpose: store governance, audit records, agent contracts, policy definitions, and evaluation results.

Recommended subfolders:
- `Policies`
- `Playbooks`
- `AuditReports`
- `AgentRegistry`

Typical use:
- agent onboarding records
- evaluation reports
- compliance policies
- audit evidence

### `AgentAssets`

Purpose: hold agent definitions, prompt templates, configuration files, onboarding guides, and model guidance.

Recommended subfolders:
- `Prompts`
- `Templates`
- `AgentConfigurations`
- `Onboarding`

Typical use:
- prompt templates for domain agents
- Master Lead prompt artifacts
- JSON definitions for agents

### `ExternalFeeds`

Purpose: ingest externally sourced content through approved connectors and controlled import jobs.

Recommended subfolders:
- `PartnerData`
- `RegulatoryFeeds`
- `MarketSignals`

Typical use:
- partner policies
- external regulatory briefs
- market intelligence feeds

## Content Types

Define the following content types in the `CopilotStudio` site collection.

### `AgentKnowledgeItem`

Fields:
- `Title`
- `BusinessUnit`
- `KnowledgeDomain`
- `ContentType`
- `SourceSystem`
- `SensitivityLabel`
- `RetentionLabel`
- `RAGPriority`
- `Language`
- `EffectiveDate`
- `ApprovedBy`
- `Summary`

Use case: generic knowledge article and RAG source.

### `PolicyDocument`

Fields:
- `Title`
- `BusinessUnit`
- `KnowledgeDomain`
- `SensitivityLabel`
- `RetentionLabel`
- `RAGPriority`
- `EffectiveDate`
- `ApprovedBy`
- `PolicyOwner`
- `ReviewCycle`

Use case: formal policy or regulation.

### `AgentBlueprint`

Fields:
- `Title`
- `BusinessUnit`
- `KnowledgeDomain`
- `SensitivityLabel`
- `ContentType`
- `LifecycleStage`
- `ResponsibleAgent`
- `Version`

Use case: agent design and capability blueprints.

### `ComplianceArtifact`

Fields:
- `Title`
- `BusinessUnit`
- `SensitivityLabel`
- `RetentionLabel`
- `ComplianceStandard`
- `ReviewDate`
- `Owner`

Use case: audit results, compliance evidence, assessment records.

### `OperationalRunbook`

Fields:
- `Title`
- `BusinessUnit`
- `KnowledgeDomain`
- `ContentType`
- `RAGPriority`
- `RunbookOwner`
- `LastTested`

Use case: procedures and operational instructions.

## Metadata Columns

This section defines the columns that must be available on the libraries used for Copilot Studio content.

### Required metadata columns

| Column | Type | Description | Example values |
|---|---|---|---|
| `BusinessUnit` | Choice | Primary business area for the content | Finance, HR, Legal, Sales, IT, Operations |
| `KnowledgeDomain` | Managed Metadata | Domain classification for RAG and routing | mCommerce, mParking, ContractManagement, Audit, Compliance |
| `ContentType` | Choice | Document role in knowledge model | Policy, Runbook, FAQ, Procedure, Contract |
| `SourceSystem` | Text | Original system source | SharePoint, ERP, CRM, Teams, External |
| `SensitivityLabel` | Choice | Classification label enforced by Purview | Public, Internal, Confidential, Highly Confidential |
| `RetentionLabel` | Choice | Retention scope for long-term management | 1 year, 3 years, 7 years, Permanent |
| `RAGPriority` | Choice | Retrieval importance for RAG ranking | High, Normal, Low |
| `Language` | Choice | Author language | en-US, local |
| `EffectiveDate` | Date | Content freshness date | 2026-05-01 |
| `ApprovedBy` | Person or Group | Compliance or content approver | Jane Doe |

### Optional metadata columns

| Column | Type | Description |
|---|---|---|
| `PolicyOwner` | Person or Group | Owner of the policy document |
| `ReviewCycle` | Choice | Review frequency for policy documents | Annual, Biennial, Quarterly |
| `LifecycleStage` | Choice | Agent asset lifecycle stage | Draft, Review, Active, Retired |
| `ResponsibleAgent` | Text | Owner or responsible agent name |
| `ComplianceStandard` | Text | Associated compliance regime | GDPR, HIPAA, ISO27001 |
| `RunbookOwner` | Person or Group | Responsible operator |
| `LastTested` | Date | Last operational test execution |

## Views and Metadata Navigation

The following views should be configured for `AgentKnowledge` and `GovernanceArtifacts`.

### Recommended `AgentKnowledge` views

1. `Finance Knowledge` — filter `BusinessUnit eq Finance`
2. `Confidential Knowledge` — filter `SensitivityLabel eq Confidential`
3. `High Priority RAG` — filter `RAGPriority eq High`
4. `Active Knowledge Domain` — filter `KnowledgeDomain is not empty`
5. `Recently Reviewed` — sort by `EffectiveDate desc`

### Recommended `GovernanceArtifacts` views

1. `Current Policies` — filter `ContentType eq PolicyDocument`
2. `Agent Registry` — filter `ContentType eq AgentBlueprint`
3. `Audit Reports` — filter `ContentType eq ComplianceArtifact`
4. `Pending Review` — filter `LifecycleStage eq Review`

## Term Store and Managed Metadata

Create a term set named `CopilotStudio Knowledge Domains` with the following top-level terms:

- `Finance`
  - `mCommerce`
  - `mParking`
  - `Treasury`
- `HR`
  - `HR Policies`
  - `Talent Operations`
- `Legal`
  - `Contract Management`
  - `Regulatory Compliance`
- `Sales`
  - `Sales Enablement`
  - `Partner Programs`
- `IT`
  - `Platform Operations`
  - `Security`
- `Operations`
  - `Service Delivery`
  - `Field Execution`

## Implementation Notes

- Use the same metadata term names in SharePoint and RAG ingestion pipelines.
- Enforce label assignment at upload time using required fields and mandatory metadata validation.
- Keep library and content type names consistent with the production naming convention to avoid tooling mismatch.
- Document all metadata changes in `GovernanceArtifacts/Policies`.
