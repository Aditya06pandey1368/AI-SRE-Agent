from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import datetime
from typing import List, Optional
import random

app = FastAPI(
    title="AI SRE Simulator",
    description="Simulated production environment for generating incidents, metrics, and logs.",
    version="1.0.0"
)

# --- State ---

class SystemState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.cpu = 40.0
        self.memory = 45.0
        self.error_rate = 0.5
        self.latency_p95 = 200.0
        self.db_connections = 20
        self.request_rate = 100.0
        self.healthy = True
        self.active_scenario = "normal"
        self.logs = []
        self.deployments = [
            {"service": "payment-api", "version": "v1.41", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()}
        ]
        self.service_versions = {"payment-api": "v1.41"}

state = SystemState()

def add_log(service: str, severity: str, message: str):
    state.logs.append({
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": service,
        "severity": severity,
        "message": message
    })
    if len(state.logs) > 1000:
        state.logs = state.logs[-1000:]

# --- Endpoints: Agent Tools ---

@app.get("/api/metrics")
def get_metrics(service: str = "payment-api"):
    # Add some random jitter
    return {
        "cpu": max(0, min(100, state.cpu + random.uniform(-2, 2))),
        "memory": max(0, min(100, state.memory + random.uniform(-1, 1))),
        "error_rate": max(0, min(100, state.error_rate + random.uniform(-0.1, 0.1))),
        "latency_p95": max(0, state.latency_p95 + random.uniform(-10, 10)),
        "db_connections": max(0, min(100, state.db_connections + random.uniform(-5, 5))),
        "request_rate": max(0, state.request_rate + random.uniform(-5, 5)),
        "healthy": state.healthy
    }

@app.get("/api/logs")
def search_logs(service: str = "payment-api", limit: int = 50):
    filtered = [log for log in state.logs if log["service"] == service]
    # In a real system, we'd filter by time and query
    return list(reversed(filtered))[:limit]

@app.get("/api/deployments")
def get_deployments(service: str = "payment-api"):
    return [d for d in state.deployments if d["service"] == service]

class RemediationRequest(BaseModel):
    action: str
    service: str
    version: Optional[str] = None
    replicas: Optional[int] = None

@app.post("/api/remediate")
def remediate(request: RemediationRequest):
    if request.action == "rollback":
        if request.version:
            state.service_versions[request.service] = request.version
            state.deployments.append({
                "service": request.service,
                "version": request.version,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            # Assume rollback fixes the bad deployment
            if state.active_scenario == "bad_deployment":
                state.reset()
                return {"status": "success", "message": f"Rolled back to {request.version}. System recovered."}
        return {"status": "success", "message": "Rollback executed"}

    if request.action == "restart":
        if state.active_scenario == "memory_leak":
            state.reset()
            return {"status": "success", "message": "Service restarted. Memory cleared."}
        return {"status": "success", "message": "Service restarted."}
        
    return {"status": "failed", "message": "Action not supported or no effect"}


# --- Endpoints: Scenario Triggers ---

@app.post("/simulate/normal")
def simulate_normal():
    state.reset()
    add_log("payment-api", "INFO", "System stabilized.")
    return {"message": "Simulating normal state"}

@app.post("/simulate/high_cpu")
def simulate_high_cpu():
    state.active_scenario = "high_cpu"
    state.cpu = 95.0
    state.error_rate = 2.0
    state.latency_p95 = 800.0
    state.healthy = False
    add_log("payment-api", "WARNING", "CPU utilization exceeded 90%")
    return {"message": "Simulating high CPU"}

@app.post("/simulate/db_exhaustion")
def simulate_db_exhaustion():
    state.active_scenario = "db_exhaustion"
    state.db_connections = 100.0
    state.error_rate = 40.0
    state.latency_p95 = 5000.0
    state.healthy = False
    add_log("payment-api", "ERROR", "Database connection pool exhausted")
    add_log("payment-api", "ERROR", "Timeout connecting to database")
    return {"message": "Simulating database connection pool exhaustion"}

@app.post("/simulate/bad_deployment")
def simulate_bad_deployment():
    state.active_scenario = "bad_deployment"
    new_version = "v1.42"
    state.service_versions["payment-api"] = new_version
    state.deployments.append({
        "service": "payment-api",
        "version": new_version,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    state.error_rate = 37.0
    state.latency_p95 = 4200.0
    state.healthy = False
    add_log("payment-api", "INFO", f"Deployment of {new_version} completed")
    add_log("payment-api", "ERROR", "NullPointerException in payment processor")
    add_log("payment-api", "ERROR", "Failed to process transaction")
    return {"message": "Simulating bad deployment"}

@app.post("/simulate/memory_leak")
def simulate_memory_leak():
    state.active_scenario = "memory_leak"
    state.memory = 98.0
    state.error_rate = 5.0
    state.healthy = False
    add_log("payment-api", "WARNING", "Memory utilization approaching 100%")
    add_log("payment-api", "ERROR", "OutOfMemoryError: Java heap space")
    return {"message": "Simulating memory leak"}
