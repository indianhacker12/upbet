from app import app, db, SlotGame

# Create slot_game table using Flask app context
with app.app_context():
    print('Creating missing tables...')
    db.create_all()
    print('Tables created successfully')
    
    # Verify if slot_game table exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    table_exists = 'slot_game' in inspector.get_table_names()
    print(f"slot_game table exists: {table_exists}")
    
    # List all tables for verification
    print("Available tables in database:")
    print(inspector.get_table_names()) 