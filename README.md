# AI SRE — Autonomous Incident Response Platform

An Agentic AI SRE platform that autonomously investigates, diagnoses, and remediates production incidents using LangGraph, LangChain, FastAPI, and React.

## What it does
When a monitoring system triggers an alert, the AI SRE agent:
1. Deterministically collects metrics, logs, and deployment events.
2. Uses an LLM to reason about the root cause using the curated evidence.
3. Plans remediation.
4. Validates the action against a deterministic safety policy.
5. Requests human approval for production-changing actions.
6. Executes the remediation.
7. Verifies recovery.
8. Generates a postmortem.

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Running Locally

Requires Docker and Docker Compose.

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in your `GROQ_API_KEY`.
3. Run `docker-compose up --build`.
4. Open `http://localhost:3000` in your browser.

## Simulator
The platform includes a simulated production environment that generates fake metrics and logs. You can use the "Simulator" tab in the dashboard to trigger scenarios like High CPU, Database Exhaustion, or Bad Deployment.
