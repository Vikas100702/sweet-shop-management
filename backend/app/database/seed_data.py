"""
Database seeding script for initial data.
Creates sample sweets and admin user for development.
"""
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.models.sweet import Sweet
from app.services.auth_service import AuthService

def create_sample_data():
    """
    Create sample data for development and testing.
    Creates admin user and initial sweet inventory.
    """
    db = SessionLocal()
    try:
        # Create admin user if doesn't exist
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@sweetshop.com",
                hashed_password=AuthService.get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            print("Created admin user (username: admin, password: admin123)")

        # Create regular test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="test@sweetshop.com",
                hashed_password=AuthService.get_password_hash("test123"),
                is_admin=False
            )
            db.add(test_user)
            print("Created test user (username: testuser, password: test123)")

        # Sample sweets data
        sample_sweets = [
            {"name": "Milk Chocolate Bar", "category": "Chocolate", "price": 2.99, "quantity": 100},
            {"name": "Dark Chocolate Truffle", "category": "Chocolate", "price": 4.99, "quantity": 50},
            {"name": "Gummy Bears", "category": "Gummy", "price": 3.49, "quantity": 75},
            {"name": "Sour Patch Kids", "category": "Sour", "price": 3.99, "quantity": 60},
            {"name": "Peppermint Hard Candy", "category": "Hard Candy", "price": 1.99, "quantity": 200},
            {"name": "Strawberry Lollipop", "category": "Lollipop", "price": 1.50, "quantity": 150},
            {"name": "Chocolate Fudge", "category": "Chocolate", "price": 5.99, "quantity": 30},
            {"name": "Rainbow Jelly Beans", "category": "Jelly", "price": 2.79, "quantity": 120},
            {"name": "Caramel Chews", "category": "Chewy", "price": 3.29, "quantity": 80},
            {"name": "Mint Chocolate Chip", "category": "Chocolate", "price": 4.49, "quantity": 45}
        ]

        # Create sweets if they don't exist
        created_count = 0
        for sweet_data in sample_sweets:
            existing_sweet = db.query(Sweet).filter(Sweet.name == sweet_data["name"]).first()
            if not existing_sweet:
                sweet = Sweet(**sweet_data)
                db.add(sweet)
                created_count += 1
        
        if created_count > 0:
            print(f"Created {created_count} sample sweets")
        else:
            print("Sample sweets already exist")

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()