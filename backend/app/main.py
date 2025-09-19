"""
Main FastAPI application for Sweet Shop Management System.
Configures routers, middleware, and application settings.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.database.connection import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Sweet Shop Management System",
    description="A comprehensive API for managing a sweet shop inventory with user authentication",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

#Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Sweet Shop Management System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "OK"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "message": "Sweet Shop API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)