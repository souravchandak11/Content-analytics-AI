"""
Content Analytics Platform - Database Connection & Session Management
=====================================================================
PostgreSQL connection pooling and session management with SQLAlchemy.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from loguru import logger

from .models import Base

# Load environment variables
load_dotenv()


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

class DatabaseConfig:
    """Database configuration from environment variables."""
    
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/content_analytics'
    )
    POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', '10'))
    MAX_OVERFLOW: int = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour
    ECHO: bool = os.getenv('DEBUG', 'False').lower() == 'true'


# =============================================================================
# ENGINE CREATION
# =============================================================================

def create_db_engine(url: str = None) -> Engine:
    """
    Create SQLAlchemy engine with connection pooling.
    
    Args:
        url: Database URL (optional, uses env var if not provided)
        
    Returns:
        SQLAlchemy Engine instance
    """
    db_url = url or DatabaseConfig.DATABASE_URL
    
    # Handle Heroku-style postgres:// URLs
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(
        db_url,
        poolclass=QueuePool,
        pool_size=DatabaseConfig.POOL_SIZE,
        max_overflow=DatabaseConfig.MAX_OVERFLOW,
        pool_timeout=DatabaseConfig.POOL_TIMEOUT,
        pool_recycle=DatabaseConfig.POOL_RECYCLE,
        pool_pre_ping=True,  # Enable connection health checks
        echo=DatabaseConfig.ECHO,
        future=True  # Use SQLAlchemy 2.0 style
    )
    
    # Log connection events in debug mode
    if DatabaseConfig.ECHO:
        @event.listens_for(engine, 'connect')
        def on_connect(dbapi_conn, connection_record):
            logger.debug(f"New database connection established")
        
        @event.listens_for(engine, 'checkout')
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug(f"Connection checked out from pool")
    
    return engine


# Global engine instance
_engine: Engine = None


def get_engine() -> Engine:
    """Get or create the global database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def create_session_factory(engine: Engine = None) -> scoped_session:
    """
    Create a thread-safe session factory.
    
    Args:
        engine: SQLAlchemy Engine (optional)
        
    Returns:
        Scoped session factory
    """
    if engine is None:
        engine = get_engine()
    
    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False  # Avoid lazy loading issues
    )
    
    return scoped_session(session_factory)


# Global session factory
_Session: scoped_session = None


def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        SQLAlchemy Session instance
        
    Note:
        Remember to close the session when done:
        session = get_session()
        try:
            # ... do work
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    """
    global _Session
    if _Session is None:
        _Session = create_session_factory()
    return _Session()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Automatically handles commit/rollback and session cleanup.
    
    Usage:
        with get_db_session() as session:
            channel = session.query(YouTubeChannel).first()
            # session auto-commits on successful exit
    """
    global _Session
    if _Session is None:
        _Session = create_session_factory()
    
    session = _Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_database(drop_existing: bool = False) -> None:
    """
    Initialize database tables.
    
    Args:
        drop_existing: If True, drop all existing tables first (DANGEROUS!)
    """
    engine = get_engine()
    
    if drop_existing:
        logger.warning("Dropping all existing tables!")
        Base.metadata.drop_all(engine)
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database connection information.
    
    Returns:
        Dictionary with database info
    """
    engine = get_engine()
    
    info = {
        'url': str(engine.url).replace(str(engine.url.password or ''), '***'),
        'driver': engine.driver,
        'pool_size': engine.pool.size(),
        'pool_checked_out': engine.pool.checkedout(),
        'pool_overflow': engine.pool.overflow(),
    }
    
    # Get table count
    try:
        with get_db_session() as session:
            result = session.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            info['table_count'] = result.scalar()
    except Exception as e:
        info['table_count'] = f"Error: {e}"
    
    return info


# =============================================================================
# CLEANUP
# =============================================================================

def cleanup() -> None:
    """Clean up database connections."""
    global _engine, _Session
    
    if _Session is not None:
        _Session.remove()
        _Session = None
    
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database connections closed")


# Register cleanup on module unload
import atexit
atexit.register(cleanup)


# =============================================================================
# INITIALIZATION SCRIPT
# =============================================================================

if __name__ == '__main__':
    """Run this script to initialize the database."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Content Analytics Database')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables first')
    parser.add_argument('--check', action='store_true', help='Only check connection')
    args = parser.parse_args()
    
    if args.check:
        success = check_database_connection()
        if success:
            info = get_database_info()
            print(f"Database Info: {info}")
        exit(0 if success else 1)
    
    init_database(drop_existing=args.drop)
    print("Database initialized successfully!")
