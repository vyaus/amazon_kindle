import sqlite3
import os, re
from flask import Flask, render_template, request, url_for, g, abort, redirect, send_from_directory

# --- Configuration ---
DATABASE = 'library.db'
DOWNLOAD_FOLDER = '../Folder'
# Note: The 'Folder' directory must exist relative to where app.py is run.

app = Flask(__name__)
app.config.from_object(__name__)

# --- Database Functions ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database structure (runs once)."""
    with app.app_context():
        db = get_db()
        # Drop table if it exists (for easy re-testing)
        db.execute('DROP TABLE IF EXISTS books')
        # Create the books table
        db.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                sn TEXT NOT NULL UNIQUE, -- Serial Number (e.g., Fiction/A16995)
                name TEXT NOT NULL,      -- Book Title
                asin TEXT                -- ASIN
            );
        """)
        # Insert some sample data (for testing)
        db.execute("INSERT INTO books (sn, name, asin) VALUES (?, ?, ?)",
                   ('NonFiction/Python_Guide', 'The Python Handbook', 'B012345678'))
        db.execute("INSERT INTO books (sn, name, asin) VALUES (?, ?, ?)",
                   ('Fiction/SciFi_Classic', '2001: A Space Odyssey', 'B00005C8I6'))
        db.commit()
        print("Database initialized and sample data added.")
        print(f"Make sure you have PDF files at: {DOWNLOAD_FOLDER}/NonFiction/Python_Guide.azw3 and {DOWNLOAD_FOLDER}/Fiction/SciFi_Classic.azw3")


# Register the close_db function to run after each request
app.teardown_appcontext(close_db)

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with search form and search results."""
    books = []
    query = ""

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            db = get_db()
            # Use LIKE for partial, case-insensitive title matching
            # The '%' acts as a wildcard
            cursor = db.execute(
                "SELECT * FROM books WHERE name LIKE ?",
                ('%' + query + '%',)
            )
            books = cursor.fetchall()

    return render_template('index.html', books=books, query=query)

def get_range_folder(sn):
    """
    Determines the 500-book range folder name based on the SN.
    E.g., A000255 -> 00001-00500
    E.g., B000501 -> 00501-01000
    """
    # 1. Extract the numeric part (e.g., '000255' from 'A000255')
    match = re.search(r'(\d+)', sn)
    if not match:
        # Handle cases where SN doesn't contain a number, if necessary
        return None 
    
    number = int(match.group(1))
    
    # 2. Calculate the start and end of the 500-book range
    # Example: number=255. (255 - 1) // 500 = 0. 0 * 500 = 0. Start = 0 + 1 = 1.
    # Example: number=501. (501 - 1) // 500 = 1. 1 * 500 = 500. Start = 500 + 1 = 501.
    range_start = ((number - 1) // 500) * 500 + 1
    range_end = range_start + 499
    
    # 3. Format the folder name (e.g., 00001-00500)
    # Use f-string formatting to ensure 5 digits with leading zeros
    folder_name = f'{range_start:05d}-{range_end:05d}'
    
    return folder_name

@app.route('/download/<path:sn>')
def download(sn):
    """Generates the file path and attempts to redirect the user to it."""

    # 1. Get the range folder (e.g., '00001-00500')
    range_folder = get_range_folder(sn)
    if not range_folder:
        abort(404, description="Invalid Serial Number format.")

    # 2. Construct the file name (e.g., 'A000255.azw3')
    filename = f'{sn}.azw3'

    # 3. Construct the full file path: 'Folder/00001-00500/A000255.azw3'
    # The os.path.join handles the slashes/backslashes correctly for all OSs
    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], range_folder, filename)
    relative_path = os.path.join(range_folder, filename)

    # IMPORTANT SECURITY NOTE: 
    # In a real-world application, you would use 'send_from_directory' for 
    # serving files securely, but for a simple example demonstrating the URL
    # generation, we'll just check existence and give a placeholder message.
    
    if not os.path.exists(filepath):
        # This part ensures the file actually exists before pretending to serve it
        # You should create the corresponding folders/files for the sample data!
        return f"Error: File not found at {filepath}. Please create it to test the download link.", 404

    # The actual download logic (requires Flask's send_from_directory for safety)
    # UNCOMMENT THE FOLLOWING LINES FOR PRODUCTION USE:
    return send_from_directory(
        directory=os.path.abspath(DOWNLOAD_FOLDER), # Absolute path to 'Folder'
        path=relative_path, # Path relative to the directory (e.g., 'Fiction/A16995.azw3')
        as_attachment=True
    )

    # For this simple example, we'll just return a success message
    # return f"Simulated download of: {sn}.azw3. (In a real app, this would trigger the download.)"

# --- Run the App ---
if __name__ == '__main__':
    # Initialize the database the first time you run this
    # Comment this out after the first run or it will reset your data!
    # init_db() 
    app.run(debug=True)
