"""
Database migration: Add streaming support columns.

This migration adds new columns for streaming response tracking:
- streaming_enabled (boolean flag)
- streaming_chunk_count (number of chunks)
- streaming_ttft_ms (time to first chunk)
- streaming_total_time_ms (total streaming duration)
- streaming_avg_inter_chunk_ms (average time between chunks)
- streaming_per_token_ms (per-token latency)

Run with: python migrations/add_streaming_support.py
"""
import sqlite3
import os


def migrate(db_path="debug_flight_recorder.db"):
    """
    Add streaming support columns to existing database.
    
    Args:
        db_path: Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        print("No migration needed - schema will be created fresh.")
        return
    
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # Streaming columns
    streaming_columns = [
        ("streaming_enabled", "BOOLEAN DEFAULT FALSE"),
        ("streaming_chunk_count", "INTEGER"),
        ("streaming_ttft_ms", "REAL"),
        ("streaming_total_time_ms", "REAL"),
        ("streaming_avg_inter_chunk_ms", "REAL"),
        ("streaming_per_token_ms", "REAL"),
    ]
    
    added_count = 0
    skipped_count = 0
    
    for col_name, col_type in streaming_columns:
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
