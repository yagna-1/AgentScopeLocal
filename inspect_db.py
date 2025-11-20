"""
Database Inspection Script
Verify the enhanced schema with provider detection and dynamic vectors.
"""
import sqlite3
import json

def inspect_database():
    conn = sqlite3.connect("debug_flight_recorder.db")
    conn.enable_load_extension(True)
    try:
        import sqlite_vec
        sqlite_vec.load(conn)
    except ImportError:
        print("Warning: sqlite-vec not available, skipping vector table inspection")
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("╔════════════════════════════════════════════╗")
    print("║  Database Inspection - Enhanced Schema    ║")
    print("╚════════════════════════════════════════════╝\n")
    
    # Check spans with provider detection
    print("📊  Spans with Provider Detection:")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            substr(span_id, 1, 8) as id,
            name,
            provider,
            model_name,
            model_family,
            prompt_tokens,
            completion_tokens,
            estimated_cost_usd
        FROM spans
        WHERE provider IS NOT NULL
        ORDER BY start_time
    """)
    
    for row in cursor.fetchall():
        print(f"  • {row['name']:<25} | Provider: {row['provider']:<12} | Model: {row['model_name']}")
        if row['prompt_tokens']:
            print(f"    Tokens: {row['prompt_tokens']} + {row['completion_tokens']} = {row['prompt_tokens'] + row['completion_tokens']}", end="")
            if row['estimated_cost_usd']:
                print(f" | Cost: ${row['estimated_cost_usd']:.6f}")
            else:
                print(" | Cost: FREE (local)")
        print()
    
    # Check vector tables
    print("\n🔢  Vector Tables (Dynamic Dimensions):")
    print("-" * 80)
    
    # Check which tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vectors_%' ORDER BY name")
    vector_tables = cursor.fetchall()
    
    for table in vector_tables:
        table_name = table['name']
        dimension = table_name.split('_')[1]
        
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        
        print(f"  • {table_name:<20} | Dimension: {dimension}  | Vectors: {count}")
    
    # Check vector metadata
    print("\n📝  Vector Metadata:")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            id,
            table_name,
            substr(content, 1, 40) as content_preview,
            metadata
        FROM vector_metadata
        ORDER BY id
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        meta = json.loads(row['metadata'])
        vector_type = meta.get('type', 'N/A')
        model = meta.get('model', 'N/A')
        print(f"  • {row['content_preview']:<42} | Table: {row['table_name']:<15} | Type: {vector_type}")
    
    # Provider summary
    print("\n📈  Provider Summary:")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            provider,
            COUNT(*) as span_count,
            SUM(prompt_tokens) as total_prompt_tokens,
            SUM(completion_tokens) as total_completion_tokens,
            SUM(estimated_cost_usd) as total_cost
        FROM spans
        WHERE provider IS NOT NULL
        GROUP BY provider
        ORDER BY span_count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  • {row['provider']:<15} | Spans: {row['span_count']:<3} | Tokens: {row['total_prompt_tokens'] or 0} + {row['total_completion_tokens'] or 0}", end="")
        if row['total_cost']:
            print(f" | Cost: ${row['total_cost']:.6f}")
        else:
            print(" | Cost: FREE")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
