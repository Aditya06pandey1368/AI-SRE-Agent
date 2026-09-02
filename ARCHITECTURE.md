# System Architecture

## Core Principle
Minimize LLM usage. Deterministic tools collect evidence, and the LLM is only used for reasoning, correlation, and planning.

## Components
1. **Frontend (React)**: Dashboard for operations, incidents, and simulator.
2. **Backend (FastAPI)**: REST API and webhook receiver.
3. **Agent Orchestrator (LangGraph)**: Stateful workflow engine driving the investigation.
4. **Simulator**: FastAPI service generating synthetic metrics, logs, and events.

## LangGraph Workflow
1. **collect_evidence**: Fetches metrics, logs, deployments.
2. **analyze_root_cause**: Calls LangChain (Llama-3/Groq) with structured output to determine root cause.
3. **policy_check**: Deterministic engine validating the proposed remediation.
4. **human_approval**: Halts execution pending human interaction.
5. **execute_remediation**: Calls the simulator to perform rollback/restart.
6. **verify_recovery**: Deterministically checks if metrics returned to normal.
7. **generate_postmortem**: Uses LLM to write a natural language report.

## Security
- External text (logs/alerts) is treated as data, preventing prompt injection from altering the agent's instructions.
- All remediation actions MUST pass the safety policy and receive human approval.
