# Typical Workflow — mParking / mCommerce

This workflow demonstrates the end-to-end implementation of an enterprise finance domain agent for mParking and mCommerce in Copilot Studio.

## Objective

Build a high-confidence Copilot Studio agent that answers finance policy and partner operation questions for the mParking / mCommerce domain while enforcing SharePoint metadata, sensitivity labeling, and audit controls.

## Step 1: Define the Domain Agent

- Agent name: `FinanceAgent_mParking_mCommerce`
- Purpose: provide finance policy guidance and operational answers for parking commerce and merchant payments.
- Allowed knowledge scope: `BusinessUnit=Finance`, `KnowledgeDomain=mCommerce`, `KnowledgeDomain=mParking`
- Sensitivity threshold: up to `Confidential`
- Required outputs:
  - short summary
  - explicit source citations
  - compliance note when label restrictions apply

## Step 2: Build SharePoint Taxonomy

### Term store values

- `Finance / mCommerce`
- `Finance / mParking`

### Content types

- `FinancePolicyDocument`
- `FinanceProcedureDocument`

### Metadata assignment

For each document:
- `BusinessUnit=Finance`
- `KnowledgeDomain=mCommerce` or `mParking`
- `ContentType=Policy` or `Procedure`
- `SensitivityLabel=Internal` or `Confidential`

## Step 3: Configure RAG Retrieval

### Ingestion metadata payload

Preserve the following fields:
- `SourceSystem=SharePoint`
- `RAGPriority=High`
- `EffectiveDate=2026-03-01`

### Retrieval filter

- `BusinessUnit eq 'Finance' AND KnowledgeDomain in ('mCommerce','mParking')`
- `SensitivityLabel ne 'Highly Confidential'`

### Ranking logic

- Select top 5 candidates.
- Rerank by:
  1. `RAGPriority`
  2. `EffectiveDate`
  3. source relevance

## Step 4: Create the Prompt Template

```text
You are FinanceAgent_mParking_mCommerce. Use only approved finance knowledge sources below. Do not invent regulatory or approval procedures.

Context:
- Requested Product: {product}
- Content filter: {metadata_filter}
- Sensitivity: {sensitivity_label}

Sources:
{top_sources}

Answer:
1. Short summary
2. Explicit source citations
3. Compliance note if any label restriction applies
```

## Step 5: Master Lead Routing

### Example route

- Request detected as: `product=mParking`, `intent=policy_lookup`
- Master Lead selects:
  - `FinanceAgent_mParking_mCommerce`
  - `RAGSpecialist`
- If the answer contains `Confidential` content, add `SecurityAuditor`.

### Metadata context attached

```json
{
  "BusinessUnit": "Finance",
  "KnowledgeDomain": "mParking",
  "ContentType": "Policy",
  "SensitivityLabel": "Internal"
}
```

## Step 6: Validation and Operation

### Production validation

- Run sample production queries:
  - “What are the latest mParking settlement rules for March 2026?”
  - “Is this mCommerce fee schedule approved for B2B partners?”
  - “Which finance approvals are needed for a merchant refund?”

### Acceptance criteria

- Answers cite SharePoint source URIs.
- No hidden confidential content is presented.
- Work IQ confidence score is ≥ 85%.

### Audit capture

Record the validation result to:
- `GovernanceArtifacts/AuditReports/mCommerce-finance-pilot.md`
