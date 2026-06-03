# Department SharePoint Knowledge Orchestration

## Overview

This document defines a Copilot Studio multi-agent architecture for SharePoint knowledge search across five organizational departments:
- `Digital Channels`
- `Development`
- `Portal`
- `Finance`
- `Fintech`

The design centers on a single Main Agent (Orchestrator) that detects query topic and routes requests to department-specific Child Agents. Each Child Agent searches only within its assigned SharePoint folder and returns precise, contextual answers with authoritative department-level expertise.

## Architecture

### Main Agent: SharePointKnowledgeOrchestrator

Responsibilities:
- Classify user queries into one or more departmental domains.
- Select the correct Child Agent(s) for the request.
- Attach SharePoint folder and metadata context to each child request.
- Merge and reconcile responses when a query overlaps multiple departments.
- Return a clean, authoritative answer with department-specific citations.

Behavior:
- Use explicit topic detection, not free-form routing.
- Enforce a department-specific boundary on each child agent.
- Keep orchestration logic separate from content generation.
- Ensure the final response clearly identifies which department(s) contributed.

### Child Agents

Each Child Agent is a department specialist and must operate independently.

Child Agent responsibilities:
- Search only within the assigned SharePoint folder.
- Use department-specific expertise to interpret query intent.
- Return factual answers grounded in SharePoint content.
- Cite the names of the folder, document, and relevant metadata used.
- If the query is outside the department's scope, return a scoped fallback such as:
  - `This question appears outside [Department] knowledge. Route to another department for a domain-specific answer.`

Example Child Agents:
- `DigitalChannelsAgent`
- `DevelopmentAgent`
- `PortalAgent`
- `FinanceAgent`
- `FintechAgent`

## Knowledge Source

Use SharePoint as the single source of truth.

Recommended structure:
- `CopilotStudio/Knowledge/DigitalChannels/`
- `CopilotStudio/Knowledge/Development/`
- `CopilotStudio/Knowledge/Portal/`
- `CopilotStudio/Knowledge/Finance/`
- `CopilotStudio/Knowledge/Fintech/`

Each folder should include:
- department metadata tags
- content type labels
- document titles, summaries, and known questions
- provenance fields for auditability

## Routing Logic

### Topic Recognition

The Orchestrator must classify each incoming query into one or more of the five departmental domains using:
- intent keywords
- domain vocabulary
- business process signals
- department-specific context words

Preferred routing model:
- Single-domain route when the query clearly belongs to one department.
- Multi-domain route when the query contains explicit overlap or compound requirements.

Examples:
- `How do I publish a news item on the corporate portal?` → `PortalAgent`
- `What are the finance approval rules for marketing campaigns?` → `FinanceAgent` + `DigitalChannelsAgent`
- `What is the API deployment process for the customer portal?` → `DevelopmentAgent` + `PortalAgent`

### Filtered SharePoint Search

For each selected Child Agent, the Orchestrator must pass a narrow SharePoint filter such as:
- `FolderPath eq '/CopilotStudio/Knowledge/Finance'`
- `Department eq 'Development'`
- `ContentType eq 'Process'`

This ensures Child Agents do not access content outside their assigned folder.

## Response Aggregation

When a query spans multiple departments, the Orchestrator should:
1. Issue the query to each relevant Child Agent with its department filter.
2. Collect answers and citations from every responding agent.
3. Merge outputs using a clear structure:
   - summary of the combined answer
   - department-specific findings
   - references to source folders or documents
4. Resolve contradictions by deferring to the agent whose expertise is most aligned with the query subtopic.

Example merged response format:
- `Digital Channels findings:` ...
- `Finance findings:` ...
- `Combined recommendation:` ...

## Department-Specific Expertise

Each Child Agent should enrich answers with knowledge that only its department can supply.

Digital Channels
- editorial publishing policies
- campaign landing page guidance
- user communication channels

Development
- implementation process, deployment standards
- integration patterns, APIs, developer handoffs

Portal
- authorization, content architecture, portal navigation
- site template and page publishing workflows

Finance
- budget approvals, cost allocation, spend governance
- financial review cycles, invoice handling

Fintech
- payment integration rules, compliance controls
- fintech product eligibility, transaction workflows

## Copilot Studio Constraints

Strict constraints:
- No external tools outside Copilot Studio orchestration.
- No actions beyond internal SharePoint search and response composition.
- No child agent may access another department's folder.
- The Main Agent must retain modular coordination and not hardcode domain content.

## Operational Rules

### Orchestrator rules
- Always classify first, then route.
- If domain classification confidence is low, route to multiple departments rather than guessing a single domain.
- Do not generate final output until child responses are complete.
- Record which folder each child agent searched.

### Child Agent rules
- Answer only from assigned SharePoint folder.
- Provide source attribution and metadata summary.
- If a query is not covered, explicitly say the question is beyond the department scope.

## Example Query Flows

### Single department
**Query:** `What is the approval process for a new fin-tech product pricing change?`
- Orchestrator routes to `FinanceAgent`.
- `FinanceAgent` searches `/Knowledge/Finance` and returns the process with citations.

### Multi-department
**Query:** `How do we update portal pricing pages and get finance sign-off?`
- Orchestrator routes to `PortalAgent` and `FinanceAgent`.
- Each agent returns scoped guidance.
- Orchestrator synthesizes a combined answer that notes both portal update steps and finance approval requirements.

## Governance and Audit

- The Orchestrator should store routing decisions and department selections for audit.
- Each child response should include explicit source references.
- Use evaluation metadata to verify that department routing was correct and that no crossover occurred.

## Summary

This architecture delivers a seamless SharePoint knowledge search experience by combining a centralized routing Orchestrator with independent, folder-bound department agents. It preserves modularity, enforces department-specific scope, and supports multi-domain queries through transparent response aggregation.