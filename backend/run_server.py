"""
Development server runner with database seeding.
Ensures database is populated with sample data on startup.
"""
import uvicorn
from app.database.seed_data import create_sample_data

if __name__ == "__main__":
    # Seed database with initial data
    print("Seeding database with initial data...")
    create_sample_data()
    
    # Start the server
    print("Starting Sweet Shop API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)