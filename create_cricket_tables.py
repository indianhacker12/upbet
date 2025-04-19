from app import app, db

# Create cricket tables using Flask app context
with app.app_context():
    print('Creating Cricket tables...')
    db.create_all()
    print('Tables created successfully')
    
    # Verify if cricket tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    cricket_tables = [
        'cricket_match',
        'cricket_match_bet',
        'cricket_event',
        'cricket_event_option',
        'cricket_event_bet'
    ]
    
    print("\nChecking Cricket tables:")
    for table in cricket_tables:
        exists = table in tables
        print(f"{table} exists: {exists}")
    
    print("\nAll tables in database:")
    print(inspector.get_table_names()) 