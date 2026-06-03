# Release Process

This release process is designed for Copilot Studio Dream Team deployments, ensuring changes are validated, governed, and rolled out safely.

## Release Tiers

### Pilot Release

- Includes small domain agent adjustments, metadata updates, or pilot knowledge refreshes.
- Validation: test queries, metadata audit, evaluation score review.
- Approval: AI Operations lead and Knowledge Governance owner.

### Production Release

- Includes new agent releases, major taxonomy changes, or security policy updates.
- Validation: full regression, security review, performance check, and Work IQ baseline validation.
- Approval: Platform Security, AI Operations, and Compliance.

## Release Steps

### 1. Change Definition

- Capture the release scope in `GovernanceArtifacts/Playbooks`.
- Associate the release with affected content types, agents, and metadata fields.
- Document rollback criteria and risk assessment.

### 2. Build & Test

- Use `scripts/deploy-sharepoint.ps1` to stage SharePoint metadata changes.
- Use `scripts/sync-metadata.ps1` to verify field consistency.
- Run `scripts/ingest-rag-data.ps1` for RAG pipeline refresh if required.
- Execute pilot queries and verify outputs.
- Confirm no sensitive content is returned without approval.

### 3. Security Review

- Validate label changes with Purview.
- Review DLP policy impacts for the new rollout.
- Confirm `MasterLead` routing changes do not bypass approval gates.

### 4. Stakeholder Approval

- Present release notes to the AI Operations team.
- Confirm business owner approval for content or agent updates.
- Obtain release signoff from Security and Compliance teams.

### 5. Deployment

- Deploy metadata and agent changes during a maintenance window.
- Monitor `Work IQ` metrics and audit logs in real time.
- Verify that the release matches documented expectations.

### 6. Post-Release Validation

- Run a production validation set of queries.
- Confirm evaluation scores are within acceptable thresholds.
- Document any post-release findings in `GovernanceArtifacts/AuditReports`.

## Rollback Criteria

Rollback if any of the following occur:
- production queries exhibit output quality regression
- unauthorized sensitive content exposure occurs
- evaluation score drops below threshold for the affected domain
- a security or compliance issue is detected

## Communication

- Notify the platform support team before release.
- Publish release notes in `GovernanceArtifacts/Policies`.
- Provide a summary to business owners and agent stewards.
