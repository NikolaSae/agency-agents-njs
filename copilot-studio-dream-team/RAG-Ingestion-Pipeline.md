# RAG Ingestion Pipeline

This document defines the hybrid RAG ingestion pipeline for Copilot Studio Dream Team.

## Goals

- Preserve SharePoint metadata through ingestion.
- Keep sensitive content out of production retrieval unless explicitly approved.
- Ensure retrieval precision with metadata-driven filters.
- Support refresh and lifecycle management.

## Pipeline Components

### 1. Source extraction

- Extract documents from `AgentKnowledge` and approved `ExternalFeeds`.
- Capture metadata for each item:
  - `BusinessUnit`
  - `KnowledgeDomain`
  - `ContentType`
  - `SensitivityLabel`
  - `RetentionLabel`
  - `RAGPriority`
  - `Language`
  - `EffectiveDate`
  - `ApprovedBy`

### 2. Chunking and embedding

- Split documents into 500–1000 token chunks.
- Include metadata in chunk payloads to preserve context.
- Use enterprise-approved embedding model and vector store.

### 3. Indexing

- Store each chunk with metadata payload in the vector store.
- Exclude items with `SensitivityLabel=Highly Confidential` from automated indexing.
- Add a `sourceUri` field for traceability.

### 4. Retrieval

- Construct retrieval queries with explicit metadata filters:
  - `BusinessUnit` and `KnowledgeDomain`
  - `SensitivityLabel` eligibility
  - `EffectiveDate` freshness constraints
  - `RAGPriority`
- Fetch top 5 candidates and rerank using business signals.

### 5. Response assembly

- Pass top results to the agent with their sources.
- Instruct the agent to cite sources verbatim.
- Append compliance notes if any sensitivity restriction applies.

## Example Metadata Payload

```json
{
  "sourceUri": "https://tenant.sharepoint.com/sites/CopilotStudio/AgentKnowledge/Finance-Policy-Approval-Workflow.docx",
  "BusinessUnit": "Finance",
  "KnowledgeDomain": "mCommerce",
  "ContentType": "Policy",
  "SensitivityLabel": "Internal",
  "RetentionLabel": "3 years",
  "RAGPriority": "High",
  "Language": "en-US",
  "EffectiveDate": "2026-03-01",
  "ApprovedBy": "Jane Doe"
}
```

## Refresh and Lifecycle

- Re-index documents when metadata changes or when `EffectiveDate` is updated.
- Remove documents from the index if they become retired, obsolete, or mislabeled.
- Use periodic health checks to detect stale vectors and orphaned metadata.

## Safety Controls

- Do not ingest `Highly Confidential` documents into production RAG indexes by default.
- Use a separate review-only index for sensitive content that requires manual approval.
- Log every ingestion event with document metadata and source URI.

## Operational Notes

- Keep ingestion scripts under `scripts/` for repeatable execution.
- Document ingestion configuration changes in `GovernanceArtifacts/Policies`.
- Use the same metadata terms across SharePoint and vector payloads to avoid mismatches.
