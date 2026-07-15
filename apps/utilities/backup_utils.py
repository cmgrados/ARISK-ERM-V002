import os
import shutil
import datetime
from django.conf import settings
from .models import DatabaseBackup

def perform_sqlite_backup(is_scheduled=False):
    db_path = settings.DATABASES['default']['NAME']
    
    # Create backups directory if it doesn't exist
    backups_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"db_backup_{timestamp}.sqlite3"
    backup_path = os.path.join(backups_dir, backup_filename)
    
    try:
        # Copy the file
        shutil.copy2(db_path, backup_path)
        
        # Get file size
        size_bytes = os.path.getsize(backup_path)
        
        # Create record in DB
        backup_record = DatabaseBackup.objects.create(
            file_name=backup_filename,
            file_path=backup_path,
            size_bytes=size_bytes,
            status='Success',
            is_scheduled=is_scheduled
        )
        return backup_record
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def restore_sqlite_backup(uploaded_file_path):
    db_path = settings.DATABASES['default']['NAME']
    
    # Make a quick safety backup of the current state before overwriting
    safety_dir = os.path.join(settings.MEDIA_ROOT, 'backups', 'safety')
    os.makedirs(safety_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safety_backup = os.path.join(safety_dir, f"db_safety_{timestamp}.sqlite3")
    shutil.copy2(db_path, safety_backup)
    
    try:
        # Overwrite the db
        shutil.copy2(uploaded_file_path, db_path)
        return True
    except Exception as e:
        # If it fails, try to restore from safety
        shutil.copy2(safety_backup, db_path)
        print(f"Restore failed: {e}")
        return False
