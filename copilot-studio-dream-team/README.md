# Copilot Studio Dream Team

This repository contains the production-ready implementation artifacts for the Copilot Studio Dream Team enterprise deployment.

## Purpose

This project codifies the architecture, metadata model, governance, and operational practices required to deploy a secure multi-agent Copilot Studio solution in a Microsoft 365 enterprise environment.

## Structure

- `architecture/` — system architecture, agent registry, security and knowledge model specifications
- `definitions/` — Master Lead prompt, agent configuration schemas, metadata templates
- `runbooks/` — setup checklist, release process, incident response
- `dashboards/` — Work IQ metrics and evaluation criteria definitions
- `scripts/` — SharePoint provisioning, metadata synchronization, RAG ingestion scripts
- `SharePoint-Structure.md` — enterprise SharePoint setup guide and metadata taxonomy
- `Typical-Workflow-mParking-mCommerce.md` — example implementation for finance domain agent
- `MasterLead-Routing-Rules.md` — routing rules for the Master Lead orchestrator
- `RAG-Ingestion-Pipeline.md` — hybrid RAG ingestion and retrieval architecture
- `Metadata-Governance-Policy.md` — metadata policy for classification, review, and lifecycle
- `architecture/department-sharepoint-knowledge-orchestration.md` — SharePoint department knowledge search orchestration design

## Getting Started

1. Review `SharePoint-Structure.md` and provision the `CopilotStudio` site collection.
2. Apply the metadata schema defined in `definitions/metadata-templates`.
3. Configure the `MasterLead` prompt in `definitions/master-lead-prompt.md`.
4. Use `scripts/deploy-sharepoint.ps1` and `scripts/sync-metadata.ps1` to build the environment.
5. Populate knowledge content and run `scripts/ingest-rag-data.ps1`.

## Maintenance

Keep this folder aligned with the enterprise governance cadence. Update the following when policies change:

- `Metadata-Governance-Policy.md`
- `MasterLead-Routing-Rules.md`
- `RAG-Ingestion-Pipeline.md`
- `workiq-metrics.md`

## Contacts

- Copilot Studio Platform Team
- Enterprise Knowledge Management Team
- Security & Compliance Operations
