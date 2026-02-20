#!/usr/bin/env python3
"""Create admin user"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user():
    """Create admin user in database"""
    engine = create_async_engine("sqlite+aiosqlite:///garage.db", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == "admin@garage.local")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("⚠️  Admin already exists")
            await engine.dispose()
            return
        
        # Create admin
        hashed_pwd = pwd_context.hash("admin123")
        admin = User(
            username="admin",
            email="admin@garage.local",
            password_hash=hashed_pwd,
            ruolo="ADMIN",
            nome="Admin",
            cognome="System",
            attivo=True
        )
        session.add(admin)
        await session.commit()
        print("✅ Admin created: admin@garage.local / admin123")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
