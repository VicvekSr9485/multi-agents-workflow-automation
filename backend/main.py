from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routes.research_route import router as research_router

# --- Load environment variables from .env ---
load_dotenv()

# Debugging: log important env vars (mask sensitive ones if needed)
print("DEBUG: GEMINI_API_KEY exists?", bool(os.getenv("GEMINI_API_KEY")))
print("DEBUG: SERPAPI_API_KEY exists?", bool(os.getenv("SERPAPI_API_KEY")))
print("DEBUG: BASE_URL =", os.getenv("BASE_URL"))
print("DEBUG: FRONTEND_URL =", os.getenv("FRONTEND_URL"))

app = FastAPI(
    title="Product Research & Report Generator API",
    description="API for researching topics and generating business reports",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # wide-open to rule out env mismatch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research_router, prefix="/api", tags=["research"])

@app.get("/")
def read_root():
    return {"message": "Product Research & Report Generator API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
