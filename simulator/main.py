from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI(
    title="AI SRE Simulator",
    description="Simulated production environment for generating incidents, metrics, and logs.",
    version="1.0.0"
)

# Simulated state
class SystemState:
    def __init__(self):
        self.cpu = 40.0
        self.memory = 45.0
        self.error_rate = 0.5
        self.latency_p95 = 200.0
        self.healthy = True
        self.active_scenario = "normal"

state = SystemState()

@app.get("/")
def root():
    return {"message": "AI SRE Simulator is running."}

@app.get("/metrics")
def get_metrics():
    return {
        "cpu": state.cpu,
        "memory": state.memory,
        "error_rate": state.error_rate,
        "latency_p95": state.latency_p95,
        "healthy": state.healthy,
        "scenario": state.active_scenario
    }
