from app import app, db

# Create all tables using Flask app context
with app.app_context():
    print('Creating all tables...')
    db.create_all()
    print('Tables created successfully')
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\nAll tables in database:")
    print(inspector.get_table_names()) 