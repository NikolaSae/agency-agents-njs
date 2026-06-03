# Metadata Governance Policy

This policy defines the requirements for SharePoint metadata, taxonomy, classification, and lifecycle management for Copilot Studio Dream Team.

## Purpose

To ensure that all knowledge content used by Copilot Studio is classified, discoverable, safe, and auditable.

## Scope

Applies to:
- `AgentKnowledge`
- `GovernanceArtifacts`
- `AgentAssets`
- `ExternalFeeds`
- Associated Copilot Studio indexes and retrieval metadata

## Mandatory Metadata Requirements

Every document uploaded to the Copilot Studio knowledge stores must include:
- `BusinessUnit`
- `KnowledgeDomain`
- `ContentType`
- `SensitivityLabel`
- `RetentionLabel`
- `RAGPriority`
- `Language`
- `EffectiveDate`
- `ApprovedBy`

Documents missing required metadata must not be indexed for production RAG use.

## Labeling Policy

### SensitivityLabel values

- `Public` — content safe for broad internal use.
- `Internal` — enterprise-only content.
- `Confidential` — content requiring review for user-facing responses.
- `Highly Confidential` — content blocked from automated retrieval without manual escalation.

### Label Enforcement

- Apply labels immediately upon upload.
- Use SharePoint mandatory column enforcement to prevent unlabeled uploads.
- Audit for unlabeled or mismatched labels weekly.

## Taxonomy Change Management

- Add new `KnowledgeDomain` terms through a documented change control process.
- Review and approve new terms with the Knowledge Governance team.
- Deprecate outdated terms and migrate associated content.
- Document taxonomy changes in `GovernanceArtifacts/Policies`.

## Metadata Quality

### Validation

- Run metadata completeness checks using `scripts/sync-metadata.ps1`.
- Report missing or inconsistent values to the Knowledge team.
- Use automated remediation scripts for common issues.

### Hygiene

- Keep `BusinessUnit` and `ContentType` choice lists short and curated.
- Avoid free-text values for classification fields where possible.
- Use managed metadata for `KnowledgeDomain` only.

## Lifecycle and Review

- `AgentKnowledge` items should be reviewed at least annually.
- `PolicyDocument` items should have a `ReviewCycle` and review date.
- Retire or archive content that is obsolete or no longer used in RAG retrieval.
- Use `RetentionLabel` to enforce data lifecycle requirements.

## Exceptions

- Exceptions must be documented in `GovernanceArtifacts/Policies/MetadataExceptions.md`.
- Temporary exceptions require an explicit owner, expiration date, and approval.
- Highly Confidential content may be excluded from RAG ingestion by policy.

## Enforcement

- Use Work IQ dashboards to monitor metadata health.
- Trigger alerts when metadata completeness drops below 95%.
- Require remediation for items with missing `SensitivityLabel` or `BusinessUnit`.

## Governance Responsibilities

- `Knowledge Governance Team` owns metadata policy.
- `AI Operations Team` enforces RAG ingestion and evaluation rules.
- `Security Team` validates label compliance and DLP policies.
- `Business Owners` approve content classifications and review cycles.
