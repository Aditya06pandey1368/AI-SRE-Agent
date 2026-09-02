from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI SRE - Autonomous Incident Response Platform API",
    description="Backend API for managing incidents and orchestrating the AI SRE agent",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to AI SRE Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
