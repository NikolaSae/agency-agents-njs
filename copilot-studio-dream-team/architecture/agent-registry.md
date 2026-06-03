# Agent Registry

This document defines the core agent registry for the Copilot Studio Dream Team implementation. The registry is the authoritative catalog of production agents, their capabilities, allowed tools, and governance requirements.

## Registry Purpose

The agent registry enables the Master Lead to make deterministic routing decisions and enforce least-privilege tool access. It also documents which agent is responsible for specific domains, security controls, and evaluation requirements.

## Core Registry Fields

Each registry entry should include:

- `agentName`
- `role`
- `capabilities`
- `modelProfile`
- `allowedTools`
- `identityType`
- `dataAccessScope`
- `securityConstraints`
- `evaluationThreshold`
- `onboardingStatus`
- `lastReviewed`

## Production Registry Entries

### Master Lead

- `agentName`: `MasterLead`
- `role`: Enterprise orchestration and governance
- `capabilities`: routing, policy enforcement, agent handoff, audit logging
- `modelProfile`: Copilot Studio Unified with custom system prompt
- `allowedTools`: Agent Registry, Tools Framework, Work IQ, Routing API
- `identityType`: managed Entra ID identity
- `dataAccessScope`: metadata read, route information, evaluation data
- `securityConstraints`: cannot directly access `Highly Confidential` content without approval
- `evaluationThreshold`: N/A (governance orchestrator)
- `onboardingStatus`: production

### Knowledge Architect

- `agentName`: `KnowledgeArchitect`
- `role`: SharePoint metadata and content model design
- `capabilities`: taxonomy design, content mapping, metadata review
- `modelProfile`: Copilot Studio Knowledge
- `allowedTools`: SharePoint REST/Graph, Content Type API, Purview API
- `identityType`: managed Entra ID identity
- `dataAccessScope`: metadata configuration, content type definitions
- `securityConstraints`: no direct content generation for user responses
- `evaluationThreshold`: N/A
- `onboardingStatus`: production

### RAG Specialist

- `agentName`: `RAGSpecialist`
- `role`: hybrid retrieval optimization and source ranking
- `capabilities`: vector search, retrieval filter construction, prompt context delivery
- `modelProfile`: Copilot Studio RAG
- `allowedTools`: Vector store connector, Azure OpenAI/GPT retrieval, SharePoint connector
- `identityType`: service principal for RAG index access
- `dataAccessScope`: read-only access to indexed content and metadata
- `securityConstraints`: cannot select sources outside authorized metadata scope
- `evaluationThreshold`: 85% retrieval relevance target
- `onboardingStatus`: production

### Orchestration Engineer

- `agentName`: `OrchestrationEngineer`
- `role`: child/connected agent pipeline design
- `capabilities`: workflow design, error handling, agent-to-agent messaging, dynamic routing
- `modelProfile`: Copilot Studio Orchestrator
- `allowedTools`: Tools Framework, evaluation hooks, agent registry write access for workflow changes
- `identityType`: managed Entra ID identity
- `dataAccessScope`: workflow definitions, metadata schemas
- `securityConstraints`: cannot bypass approval workflows
- `evaluationThreshold`: N/A
- `onboardingStatus`: production

### Security & Compliance Auditor

- `agentName`: `SecurityAuditor`
- `role`: DLP, sensitivity, audit review
- `capabilities`: classify content, validate labels, approve or reject responses
- `modelProfile`: Copilot Studio Security
- `allowedTools`: Entra ID, Purview, DLP scanner, audit log access
- `identityType`: managed Entra ID identity with elevated review permissions
- `dataAccessScope`: sensitive content metadata, audit logs
- `securityConstraints`: no direct user response generation unless explicitly approved
- `evaluationThreshold`: 100% safety verification for `Confidential` responses
- `onboardingStatus`: production

### Work IQ Analyst

- `agentName`: `WorkIQAnalyst`
- `role`: analytics, evaluation, drift detection
- `capabilities`: metric definition, scoring thresholds, anomaly detection
- `modelProfile`: Copilot Studio Insights
- `allowedTools`: Work IQ dashboards, telemetry query APIs, evaluation APIs
- `identityType`: managed Entra ID identity
- `dataAccessScope`: request logs, evaluation outcomes, trend data
- `securityConstraints`: read-only analytics access
- `evaluationThreshold`: configurable by domain
- `onboardingStatus`: production

### SharePoint Metadata Architect

- `agentName`: `SharePointMetadataArchitect`
- `role`: advanced metadata navigation and taxonomy operations
- `capabilities`: configure managed metadata, content types, view definitions
- `modelProfile`: Copilot Studio Knowledge
- `allowedTools`: SharePoint taxonomy API, content type API, metadata navigation configuration
- `identityType`: managed Entra ID identity
- `dataAccessScope`: SharePoint metadata configuration
- `securityConstraints`: no direct content generation for end users
- `evaluationThreshold`: N/A
- `onboardingStatus`: production

### Enterprise Domain Agent

- `agentName`: `EnterpriseDomainAgent`
- `role`: business domain delivery for finance, HR, legal, sales, etc.
- `capabilities`: domain-specific response generation, source citation, compliance context
- `modelProfile`: Copilot Studio Agents with domain prompt templates
- `allowedTools`: domain connectors, RAG sources, SharePoint query API
- `identityType`: managed Entra ID identity or domain-scoped service principal
- `dataAccessScope`: authorized domain content and metadata
- `securityConstraints`: cannot bypass security approval for sensitive responses
- `evaluationThreshold`: 85% answer confidence target
- `onboardingStatus`: pilot / production based on domain

## Registry Maintenance

- Review registry entries quarterly.
- Add new agents only after a documented business use case and approval.
- Mark retired agents as `onboardingStatus: retired` and remove tool permissions.
- Use `GovernanceArtifacts/AgentRegistry` to store the registry and change log.
