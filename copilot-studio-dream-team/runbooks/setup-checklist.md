# Setup Checklist

A step-by-step checklist to provision and launch the Copilot Studio Dream Team pilot.

## Phase 0: Foundation

- [ ] Confirm Microsoft 365 tenant has Copilot Studio enabled
- [ ] Confirm Microsoft Purview licensing and tenant configuration
- [ ] Confirm Entra ID admin access and service principal creation rights
- [ ] Create SharePoint site collection `CopilotStudio`
- [ ] Create `AgentKnowledge`, `GovernanceArtifacts`, `AgentAssets`, and `ExternalFeeds` libraries
- [ ] Configure SharePoint term store and metadata navigation
- [ ] Deploy content types from `definitions/metadata-templates/content-types.json`
- [ ] Deploy metadata fields from `definitions/metadata-templates/sharepoint-columns.json`
- [ ] Create required views for `AgentKnowledge` and `GovernanceArtifacts`
- [ ] Configure Purview sensitivity labels and DLP policies
- [ ] Create initial `AgentRegistry` folder in `GovernanceArtifacts`
- [ ] Register the core agents in the registry with identity and tool mapping
- [ ] Deploy the Master Lead prompt from `definitions/master-lead-prompt.md`
- [ ] Build the first RAG ingestion pipeline and validate initial retrieval

## Phase 1: Pilot

- [ ] Seed `AgentKnowledge` with 25–40 production documents
- [ ] Confirm metadata completeness for each seeded document
- [ ] Build a pilot domain agent (Finance, HR, or Legal)
- [ ] Configure explicit retrieval filters and label enforcement
- [ ] Run 20 pilot queries and validate responses
- [ ] Verify all answers include explicit source citations
- [ ] Verify no `Highly Confidential` content is exposed automatically
- [ ] Configure Work IQ dashboards and baseline metrics
- [ ] Confirm evaluation hooks are active for all pilot responses

## Phase 2: Governance Hardening

- [ ] Map each agent to a dedicated Entra ID identity or service principal
- [ ] Review and tighten permission scopes for tool access
- [ ] Implement Security Auditor approval gating for confidential results
- [ ] Enable auditing of all `MasterLead` routes and tool calls
- [ ] Document audit trail retention requirements in `GovernanceArtifacts`
- [ ] Validate DLP policy enforcement via simulated sensitive queries
- [ ] Archive or remediate any unlabeled content found in `AgentKnowledge`

## Phase 3: Scale

- [ ] Add at least one additional domain agent
- [ ] Deploy `AgentLifecycleManager` rules for retirements and updates
- [ ] Establish quarterly knowledge taxonomy reviews
- [ ] Add a `Knowledge Quality Agent` for metadata hygiene
- [ ] Implement regular Work IQ health checks and drift detection
- [ ] Schedule governance reviews with security, AI ops, and knowledge teams

## Post-Deployment Verification

- [ ] Document the first production support runbook
- [ ] Confirm backup/recovery procedures for SharePoint and RAG index
- [ ] Create a change control process for metadata updates
- [ ] Publish this checklist as part of the Copilot Studio project documentation
