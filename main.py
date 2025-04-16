from fastapi import FastAPI
from api.routes import router
from core.config import Config
from fastapi.middleware.cors import CORSMiddleware

# Initialize config
config = Config()

# Create FastAPI app
app = FastAPI(
    title="Story Writer API",
    description="API for generating stories about places",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Add a root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Story Writer API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 