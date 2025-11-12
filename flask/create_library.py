import sqlite3
import os

# --- Configuration ---
# Must match the database file used by library_manager.py
DATABASE = 'library.db'
# Name of the file containing the book list data
INPUT_FILE = 'book_list.txt'
# --- End Configuration ---

def create_connection(db_file):
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # Ensure robust UTF-8 handling
        conn.text_factory = str 
        # For efficiency, set the connection to manual commit mode
        conn.isolation_level = None
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def setup_database(conn):
    """
    Create the 'books' table if it doesn't exist, updated for ASIN and 
    with the 'path' column removed as requested.
    """
    sql_create_books_table = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        sn TEXT NOT NULL UNIQUE, -- Serial Number (full path segment, e.g., Fiction/A16995)
        name TEXT NOT NULL,      -- Book Title
        asin TEXT                -- Amazon Standard Identification Number
    );
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_books_table)
        # Ensure index exists for efficient lookups/updates
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_books_sn ON books (sn);")
    except sqlite3.Error as e:
        print(f"Error setting up table and index: {e}")

def parse_line(line):
    """
    Parses a line formatted as 'path/sn\ttitle\tasin'
    into (sn, name, asin).
    """
    line = line.strip()
    if not line:
        return None

    # Split the line into exactly three parts based on the tab character
    parts = line.split('\t') 
    
    if len(parts) != 3:
        print(f"Skipping line due to invalid format (expected exactly two tab delimiters): {line}")
        return None

    # Assign and strip whitespace from each part
    path_segment, name, asin = [p.strip() for p in parts]
    
    # 1. Assign SN (Serial Number)
    # The full path segment is used as the unique identifier (sn) for the record.
    sn = path_segment 
    
    # NOTE: The 'path' variable is no longer constructed or stored in the database.

    if not sn or not name or not asin:
        print(f"Skipping line due to missing required component after parsing: {line}")
        return None

    # Result: (sn, name, asin)
    return (sn, name, asin)

def import_data(conn, filename=INPUT_FILE):
    """
    Reads the input file and performs an UPSERT (UPDATE or INSERT) 
    based on the unique 'sn' (Serial Number).
    """
    books_to_upsert = []
    
    if not os.path.exists(filename):
        print(f"Error: Input file '{filename}' not found. Please create it first.")
        return

    print(f"Reading data from '{filename}'...")
    try:
        # Use utf-8 encoding to handle Chinese characters
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                book_data = parse_line(line)
                if book_data:
                    # book_data is now (sn, name, asin)
                    books_to_upsert.append(book_data)
    except Exception as e:
        print(f"Error reading or parsing input file: {e}")
        return

    if not books_to_upsert:
        print("No valid book entries found to import.")
        return

    print(f"Found {len(books_to_upsert)} book entries. Performing UPSERT based on 'sn'...")

    # UPSERT statement: Insert 3 values (sn, name, asin). 
    # If 'sn' conflicts, update the 'name', and 'asin' columns.
    sql_upsert = """
    INSERT INTO books (sn, name, asin) VALUES (?, ?, ?)
    ON CONFLICT(sn) DO UPDATE SET 
        name = excluded.name, 
        asin = excluded.asin;
    """
    
    try:
        cursor = conn.cursor()
        # Use executemany for efficient bulk insertion/update
        cursor.executemany(sql_upsert, books_to_upsert)
        
        # Commit all changes to the database
        conn.commit() 
        
        print(f"Successfully processed {cursor.rowcount} records (inserts and updates).")
    except sqlite3.Error as e:
        print(f"Database UPSERT error: {e}")
        conn.rollback()
        
def main():
    
    # Check if the real data file exists
    if not os.path.exists(INPUT_FILE):
        print(f"""
============================================================
ACTION REQUIRED:
The input file '{INPUT_FILE}' was not found. 
Please create this file and populate it with your 
real book data, using the TAB-DELIMITED format: 
[full_path_segment]\\t[book_title]\\t[ASIN]
(The full path segment is used as the unique ID in the database.)
Example: Fiction/Classics/A16995\\t认知迭代：自由切换大脑的思考模式\\tB07KM86G4L
============================================================
""")
        return
    
    # 2. Connect to DB and Import
    conn = create_connection(DATABASE)
    if conn:
        setup_database(conn)
        import_data(conn)
        conn.close()
        print("\nImport process complete. Check 'library.db' for updated data.")

if __name__ == '__main__':
    main()
