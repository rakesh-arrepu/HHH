"""Backup service for database backups and log management."""

import os
import subprocess
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.backup_log import BackupLog, BackupStatus
from core.database import engine


def trigger_backup(db: Session, user_id: str) -> Dict[str, Any]:
    """Trigger a database backup (Super Admin only)."""
    try:
        # Generate backup filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = f"/tmp/{backup_filename}"

        # Use pg_dump for PostgreSQL or sqlite3 for SQLite
        if "postgresql" in str(engine.url):
            # PostgreSQL backup
            db_url = str(engine.url)
            # Extract connection details from URL
            cmd = [
                "pg_dump",
                "--no-owner",
                "--no-privileges",
                "--clean",
                "--if-exists",
                "--format=custom",
                str(engine.url),
                "-f", backup_path
            ]
        else:
            # SQLite backup (development) - file copy fallback (no sqlite3 CLI dependency)
            db_path = engine.url.database
            import shutil
            shutil.copyfile(db_path, backup_path)
            backup_size = os.path.getsize(backup_path)

            # Log successful backup
            backup_log = BackupLog(
                backup_file=backup_filename,
                backup_size=backup_size,
                status=BackupStatus.SUCCESS
            )
            db.add(backup_log)
            db.commit()
            db.refresh(backup_log)

            # Clean up local file (in production, this would be uploaded to cloud storage)
            if os.path.exists(backup_path):
                os.remove(backup_path)

            return {
                "success": True,
                "message": "Backup completed successfully",
                "backup_file": backup_filename,
                "backup_size": backup_size,
                "backup_id": backup_log.id
            }

        # Execute backup command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            # Get backup file size
            backup_size = os.path.getsize(backup_path)

            # Log successful backup
            backup_log = BackupLog(
                backup_file=backup_filename,
                backup_size=backup_size,
                status=BackupStatus.SUCCESS
            )
            db.add(backup_log)
            db.commit()
            db.refresh(backup_log)

            # Clean up local file (in production, this would be uploaded to cloud storage)
            if os.path.exists(backup_path):
                os.remove(backup_path)

            return {
                "success": True,
                "message": "Backup completed successfully",
                "backup_file": backup_filename,
                "backup_size": backup_size,
                "backup_id": backup_log.id
            }
        else:
            # Log failed backup
            backup_log = BackupLog(
                backup_file=backup_filename,
                backup_size=0,
                status=BackupStatus.FAILED
            )
            db.add(backup_log)
            db.commit()

            return {
                "success": False,
                "message": f"Backup failed: {result.stderr}",
                "backup_file": backup_filename
            }

    except Exception as e:
        # Log failed backup on exception
        try:
            backup_log = BackupLog(
                backup_file=f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.sql",
                backup_size=0,
                status=BackupStatus.FAILED
            )
            db.add(backup_log)
            db.commit()
        except:
            pass  # Don't fail if logging fails

        return {
            "success": False,
            "message": f"Backup failed with exception: {str(e)}"
        }


def get_backup_logs(db: Session, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get backup operation logs."""
    logs = db.query(BackupLog).order_by(BackupLog.created_at.desc()).offset(offset).limit(limit).all()

    return [{
        "id": log.id,
        "backup_file": log.backup_file,
        "backup_size": log.backup_size,
        "status": str(log.status),
        "created_at": log.created_at.isoformat()
    } for log in logs]


def get_backup_stats(db: Session) -> Dict[str, Any]:
    """Get backup statistics."""
    total_backups = db.query(BackupLog).count()
    successful_backups = db.query(BackupLog).filter_by(status=BackupStatus.SUCCESS).count()
    failed_backups = db.query(BackupLog).filter_by(status=BackupStatus.FAILED).count()

    # Get total backup size
    from sqlalchemy import func
    total_size_result = db.query(func.sum(BackupLog.backup_size)).filter_by(status=BackupStatus.SUCCESS).scalar()
    total_size = total_size_result or 0

    # Get latest backup
    latest_backup = db.query(BackupLog).filter_by(status=BackupStatus.SUCCESS).order_by(BackupLog.created_at.desc()).first()

    return {
        "total_backups": total_backups,
        "successful_backups": successful_backups,
        "failed_backups": failed_backups,
        "total_backup_size": total_size,
        "latest_backup": {
            "file": latest_backup.backup_file if latest_backup else None,
            "size": latest_backup.backup_size if latest_backup else None,
            "created_at": latest_backup.created_at.isoformat() if latest_backup else None
        } if latest_backup else None
    }
