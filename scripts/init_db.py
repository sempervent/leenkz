#!/usr/bin/env python3
"""Initialize the database for development."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
import asyncio

from leenkz.core.seed import seed_database


def run_migrations():
    """Run database migrations synchronously."""
    print("📦 Running database migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations completed successfully")


async def init_database():
    """Initialize the database with migrations and seed data."""
    print("🚀 Initializing Leenkz database...")
    
    try:
        # Run migrations synchronously
        run_migrations()
        
        # Seed database with sample data
        print("🌱 Seeding database with sample data...")
        await seed_database()
        print("✅ Database seeded successfully")
        
        print("🎉 Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    asyncio.run(init_database())


if __name__ == "__main__":
    main() 