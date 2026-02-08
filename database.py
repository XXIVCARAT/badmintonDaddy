"""
Database initialization and migration utilities.
"""
from sqlalchemy import text, inspect
from flask import Flask
from models import db, Player, LikeCounter, Comment


INITIAL_PLAYERS = [
    "Manan", "Ourab", "Anuj", "Suhal", "Sujay", "Harshil",
    "Shreyas", "Ishita", "Idhant", "Chirag", "Nirlep", "Ameya"
]


def run_migrations(app: Flask) -> None:
    """
    Check for new columns and add them if they don't exist.
    Preserves existing data while upgrading the schema.
    """
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('player')]
        
        new_cols = [
            ('singles_played', 'INTEGER DEFAULT 0'),
            ('singles_lost', 'INTEGER DEFAULT 0'),
            ('doubles_played', 'INTEGER DEFAULT 0'),
            ('doubles_lost', 'INTEGER DEFAULT 0')
        ]
        
        with db.engine.connect() as conn:
            for col_name, col_type in new_cols:
                if col_name not in columns:
                    print(f"Migrating: Adding {col_name} to Player table...")
                    conn.execute(text(f'ALTER TABLE player ADD COLUMN {col_name} {col_type}'))
                    conn.commit()


def init_db(app: Flask) -> None:
    """
    Initialize the database: create tables and seed initial data.
    """
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Run migrations for existing databases
        run_migrations(app)
        
        # Seed initial players if database is empty
        if not Player.query.first():
            print("Seeding initial players...")
            for name in INITIAL_PLAYERS:
                db.session.add(Player(name=name))
            db.session.commit()
        
        # Initialize like counter if it doesn't exist
        if not LikeCounter.query.first():
            print("Initializing like counter...")
            db.session.add(LikeCounter(count=0))
            db.session.commit()


def reset_db(app: Flask) -> None:
    """
    Drop all tables and reinitialize (use with caution!).
    """
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        init_db(app)
