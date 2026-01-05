import os
from sqlalchemy import create_engine
from .database import Base

# Set the DATABASE_URL for Neon
DATABASE_URL = 'postgresql://neondb_owner:npg_qH4WkN3LaDhv@ep-lingering-rice-a19h4m3w-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

# Normalize to use psycopg (psycopg3)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Import models to register them with Base
from .models import User, Group, GroupMember, Entry, ActivityType, HealthActivity, UserActivityFavorite

# Create engine and create tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
