import sqlite3
import sqlite_vec
import json

def verify():
    conn = sqlite3.connect("debug_flight_recorder.db")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    
    cursor = conn.cursor()
    
    print("--- Spans ---")
    cursor.execute("SELECT name, trace_id, span_id FROM spans")
    spans = cursor.fetchall()
    for s in spans:
        print(s)
        
    print("\n--- Vector Metadata ---")
    cursor.execute("SELECT trace_id, span_id, text_content FROM vector_metadata")
    metas = cursor.fetchall()
    for m in metas:
        print(m)

    print("\n--- Vectors ---")
    cursor.execute("SELECT rowid FROM debug_vectors")
    vectors = cursor.fetchall()
    print(f"Vector count: {len(vectors)}")

    conn.close()

if __name__ == "__main__":
    verify()
