# Work IQ Metrics

This document defines the core Work IQ metrics for the Copilot Studio Dream Team deployment.

## Metric Categories

### 1. Agent Performance

- `Agent Request Volume` — number of requests handled by each agent per day.
- `Agent Response Latency` — average time between request arrival and final response.
- `Agent Route Accuracy` — percentage of requests routed to the correct agent on first pass.

### 2. Knowledge Quality

- `High Priority Source Utilization` — percentage of RAG answers that cite `RAGPriority=High` documents.
- `Metadata Completeness` — percentage of knowledge items with required metadata fields populated.
- `Outdated Content Fraction` — percentage of items with `EffectiveDate` older than 12 months.

### 3. Security & Compliance

- `Sensitive Query Count` — number of queries requiring `Confidential` or `Highly Confidential` handling.
- `Security Auditor Interventions` — count of responses routed to the Security Auditor.
- `Policy Exception Rate` — percentage of answers flagged for policy review.

### 4. Evaluation & Drift

- `Average Evaluation Score` — mean score from evaluation hooks across all responses.
- `Low Confidence Rate` — percentage of responses below the confidence threshold.
- `Drift Alerts` — number of detected changes in answer quality or source relevance.

## Recommended Dashboard Views

### Agent Operations Dashboard

- `Agent Request Volume`
- `Agent Response Latency`
- `Agent Route Accuracy`
- `Security Auditor Interventions`

### Knowledge Health Dashboard

- `Metadata Completeness`
- `Outdated Content Fraction`
- `High Priority Source Utilization`
- `Sensitive Query Count`

### Compliance Dashboard

- `Policy Exception Rate`
- `Sensitive Query Count`
- `Security Auditor Interventions`
- `Audit Log Events`

### Quality Assurance Dashboard

- `Average Evaluation Score`
- `Low Confidence Rate`
- `Drift Alerts`
- `Evaluation Trends by Domain`

## Implementation Guidance

- Tie Work IQ metrics directly to the `MasterLead` orchestration logs.
- Use `BusinessUnit` and `KnowledgeDomain` dimensions for all major metrics.
- Capture evaluation and compliance labels as discrete fields for analysis.
- Refresh dashboards hourly during pilot launch and daily in steady state.
