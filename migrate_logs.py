import os
import shutil
from pathlib import Path

def migrate_logs():
    """Move existing JSON logs to output/logs directory."""
    output_base = Path("./output")
    logs_base = output_base / "logs"
    
    print(f"Migrating logs from {output_base} to {logs_base}...")
    
    # Ensure logs base exists
    logs_base.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    
    # Find all JSON files in output subdirectories (excluding logs itself)
    for file_path in output_base.rglob("*.json"):
        # Skip files already in logs directory
        if "logs" in file_path.parts:
            continue
            
        # Determine relative path from output base (e.g., "Tranche 1/file.json")
        rel_path = file_path.relative_to(output_base)
        
        # Construct new path: output/logs/Tranche 1/file.json
        new_path = logs_base / rel_path
        
        # Ensure parent directory exists (e.g., output/logs/Tranche 1)
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file
        print(f"Moving {file_path} -> {new_path}")
        shutil.move(str(file_path), str(new_path))
        moved_count += 1
        
    print(f"\nMigration complete. Moved {moved_count} log files.")

if __name__ == "__main__":
    migrate_logs()
