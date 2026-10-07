import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "library.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('librarian','student'))
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        total_copies INTEGER NOT NULL,
        available_copies INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        fine INTEGER DEFAULT 0,
        FOREIGN KEY(book_id) REFERENCES books(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    );
    """)

    users = [
        ("librarian", "admin123", "librarian"),
        ("student1", "student123", "student"),
        ("student2", "student123", "student")
    ]
    for user in users:
        db.execute(
            "INSERT OR IGNORE INTO users(username,password,role) VALUES(?,?,?)",
            user
        )

    sample_books = [
        ("Python Programming", "Eric Matthes", "Programming", 5),
        ("Database System Concepts", "Silberschatz", "Database", 3),
        ("Computer Networks", "Andrew S. Tanenbaum", "Networking", 4),
        ("Artificial Intelligence", "Stuart Russell", "AI", 2)
    ]
    for title, author, category, copies in sample_books:
        exists = db.execute(
            "SELECT id FROM books WHERE title=?", (title,)
        ).fetchone()
        if not exists:
            db.execute("""
                INSERT INTO books(title,author,category,total_copies,available_copies)
                VALUES(?,?,?,?,?)
            """, (title, author, category, copies, copies))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
