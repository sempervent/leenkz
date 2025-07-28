"""Database seeding script."""

import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from leenkz.core.auth import get_password_hash
from leenkz.core.database import AsyncSessionLocal, Link, LinkTag, Share, Tag, User


async def seed_database() -> None:
    """Seed the database with sample data."""
    async with AsyncSessionLocal() as session:
        # Create sample users
        users = [
            User(
                email="admin@leenkz.dev",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
            ),
            User(
                email="user@leenkz.dev",
                username="user",
                hashed_password=get_password_hash("user123"),
                is_active=True,
                is_superuser=False,
            ),
            User(
                email="demo@leenkz.dev",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_superuser=False,
            ),
        ]
        
        for user in users:
            session.add(user)
        await session.commit()
        
        # Get users for foreign keys
        admin_user = await session.execute(select(User).where(User.username == "admin"))
        admin_user = admin_user.scalar_one()
        
        demo_user = await session.execute(select(User).where(User.username == "demo"))
        demo_user = demo_user.scalar_one()
        
        # Create sample tags
        tags = [
            Tag(name="python", color="#3776ab", user_id=admin_user.id),
            Tag(name="fastapi", color="#009688", user_id=admin_user.id),
            Tag(name="react", color="#61dafb", user_id=admin_user.id),
            Tag(name="typescript", color="#3178c6", user_id=admin_user.id),
            Tag(name="docker", color="#2496ed", user_id=admin_user.id),
            Tag(name="aws", color="#ff9900", user_id=admin_user.id),
            Tag(name="tutorial", color="#ff6b6b", user_id=demo_user.id),
            Tag(name="blog", color="#4ecdc4", user_id=demo_user.id),
        ]
        
        for tag in tags:
            session.add(tag)
        await session.commit()
        
        # Create sample links
        links = [
            Link(
                url="https://fastapi.tiangolo.com/",
                title="FastAPI - Modern, fast web framework for building APIs with Python",
                description="FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.",
                user_id=admin_user.id,
            ),
            Link(
                url="https://react.dev/",
                title="React – A JavaScript library for building user interfaces",
                description="React is the library for web and native user interfaces. Build user interfaces out of individual pieces called components written in JavaScript.",
                user_id=admin_user.id,
            ),
            Link(
                url="https://www.typescriptlang.org/",
                title="TypeScript: JavaScript With Syntax For Types",
                description="TypeScript is a strongly typed programming language that builds on JavaScript, giving you better tooling at any scale.",
                user_id=admin_user.id,
            ),
            Link(
                url="https://docs.docker.com/",
                title="Docker Documentation",
                description="Learn how to use Docker to package and run applications in a loosely isolated environment called a container.",
                user_id=admin_user.id,
            ),
            Link(
                url="https://aws.amazon.com/",
                title="Amazon Web Services (AWS) - Cloud Computing Services",
                description="Amazon Web Services offers reliable, scalable, and inexpensive cloud computing services.",
                user_id=demo_user.id,
            ),
            Link(
                url="https://realpython.com/",
                title="Real Python – Python Tutorials, Courses, and Books",
                description="Learn Python programming with tutorials, courses, and books from Real Python.",
                user_id=demo_user.id,
            ),
        ]
        
        for link in links:
            session.add(link)
        await session.commit()
        
        # Create link-tag associations
        link_tag_associations = [
            LinkTag(link_id=1, tag_id=1),  # FastAPI - python
            LinkTag(link_id=1, tag_id=2),  # FastAPI - fastapi
            LinkTag(link_id=2, tag_id=3),  # React - react
            LinkTag(link_id=2, tag_id=4),  # React - typescript
            LinkTag(link_id=3, tag_id=4),  # TypeScript - typescript
            LinkTag(link_id=4, tag_id=5),  # Docker - docker
            LinkTag(link_id=5, tag_id=6),  # AWS - aws
            LinkTag(link_id=6, tag_id=7),  # Real Python - tutorial
            LinkTag(link_id=6, tag_id=8),  # Real Python - blog
        ]
        
        for association in link_tag_associations:
            session.add(association)
        await session.commit()
        
        # Create sample shares
        shares = [
            Share(
                link_id=1,
                shared_by=admin_user.id,
                shared_with=demo_user.id,
                message="Check out this awesome FastAPI framework!",
            ),
            Share(
                link_id=6,
                shared_by=demo_user.id,
                shared_with=admin_user.id,
                message="Great resource for learning Python",
            ),
        ]
        
        for share in shares:
            session.add(share)
        await session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created {len(users)} users, {len(tags)} tags, {len(links)} links")
        print("Sample users:")
        print("  - admin@leenkz.dev / admin123")
        print("  - user@leenkz.dev / user123")
        print("  - demo@leenkz.dev / demo123") 