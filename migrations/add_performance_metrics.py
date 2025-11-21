"""
Database migration: Add performance metrics columns.

This migration adds new columns for:
- Performance metrics (TTFT, TPS, generation time)
- Model configuration (temperature, top_p, max_tokens, etc.)
- Resource monitoring (CPU, memory, GPU)

Run with: python migrations/add_performance_metrics.py
"""
import sqlite3
import os


def migrate(db_path="debug_flight_recorder.db"):
    """
    Add performance metrics columns to existing database.
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        print("No migration needed - schema will be created fresh.")
        return
    
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # Performance metrics columns
    performance_columns = [
        ("ttft_ms", "REAL"),
        ("tokens_per_second", "REAL"),
        ("generation_time_ms", "REAL"),
    ]
    
    # Model configuration columns
    config_columns = [
        ("temperature", "REAL"),
        ("top_p", "REAL"),
        ("top_k", "INTEGER"),
        ("max_tokens", "INTEGER"),
        ("context_window_size", "INTEGER"),
    ]
    
    # Resource monitoring columns
    resource_columns = [
        ("cpu_percent", "REAL"),
        ("memory_mb", "REAL"),
        ("gpu_utilization", "REAL"),
        ("gpu_memory_used_mb", "REAL"),
    ]
    
    all_columns = performance_columns + config_columns + resource_columns
    
    added_count = 0
    skipped_count = 0
    
    for col_name, col_type in all_columns:
        try:
            conn.execute(f"ALTER TABLE spans ADD COLUMN {col_name} {col_type}")
            print(f"  ✓ Added column: {col_name} ({col_type})")
            added_count += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"  - Column already exists: {col_name}")
                skipped_count += 1
            else:
                print(f"  ✗ Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete!")
    print(f"  Added: {added_count} columns")
    print(f"  Skipped: {skipped_count} columns (already exist)")


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "debug_flight_recorder.db"
    migrate(db_path)
