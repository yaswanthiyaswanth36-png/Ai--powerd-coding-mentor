from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from database import init_db, get_db
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "library-management-secret-key"

DUE_DAYS = 14

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def index():
    return redirect(url_for("dashboard")) if "user_id" in session else redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required()
def dashboard():
    db = get_db()
    books = db.execute("SELECT * FROM books ORDER BY title").fetchall()

    if session["role"] == "student":
        issued = db.execute("""
            SELECT issues.*, books.title, books.author
            FROM issues JOIN books ON issues.book_id = books.id
            WHERE issues.student_id=? AND issues.return_date IS NULL
            ORDER BY issues.due_date
        """, (session["user_id"],)).fetchall()
        return render_template("student_dashboard.html", books=books, issued=issued)

    issues = db.execute("""
        SELECT issues.*, books.title, users.username
        FROM issues
        JOIN books ON issues.book_id=books.id
        JOIN users ON issues.student_id=users.id
        ORDER BY issues.issue_date DESC
    """).fetchall()
    return render_template("librarian_dashboard.html", books=books, issues=issues)

@app.route("/books", methods=["GET", "POST"])
@login_required("librarian")
def books():
    db = get_db()
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        category = request.form["category"].strip()
        copies = int(request.form["copies"])
        db.execute(
            "INSERT INTO books(title,author,category,total_copies,available_copies) VALUES(?,?,?,?,?)",
            (title, author, category, copies, copies)
        )
        db.commit()
        flash("Book added successfully.")
        return redirect(url_for("dashboard"))
    return render_template("book_form.html", book=None)

@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
@login_required("librarian")
def edit_book(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not book:
        flash("Book not found.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        category = request.form["category"].strip()
        new_total = int(request.form["copies"])
        issued_count = book["total_copies"] - book["available_copies"]
        if new_total < issued_count:
            flash(f"Copies cannot be less than currently issued copies ({issued_count}).")
            return render_template("book_form.html", book=book)
        available = new_total - issued_count
        db.execute("""
            UPDATE books SET title=?, author=?, category=?, total_copies=?, available_copies=?
            WHERE id=?
        """, (title, author, category, new_total, available, book_id))
        db.commit()
        flash("Book updated successfully.")
        return redirect(url_for("dashboard"))
    return render_template("book_form.html", book=book)

@app.route("/books/delete/<int:book_id>")
@login_required("librarian")
def delete_book(book_id):
    db = get_db()
    active = db.execute(
        "SELECT COUNT(*) AS c FROM issues WHERE book_id=? AND return_date IS NULL",
        (book_id,)
    ).fetchone()["c"]
    if active:
        flash("Cannot delete a book that is currently issued.")
    else:
        db.execute("DELETE FROM books WHERE id=?", (book_id,))
        db.commit()
        flash("Book deleted.")
    return redirect(url_for("dashboard"))

@app.route("/search")
@login_required()
def search():
    q = request.args.get("q", "").strip()
    db = get_db()
    books = db.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
        ORDER BY title
    """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    return render_template("search.html", books=books, q=q)

@app.route("/issue/<int:book_id>", methods=["POST"])
@login_required("librarian")
def issue_book(book_id):
    student_username = request.form["student_username"].strip()
    db = get_db()
    student = db.execute(
        "SELECT * FROM users WHERE username=? AND role='student'",
        (student_username,)
    ).fetchone()
    book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()

    if not student:
        flash("Student username not found.")
        return redirect(url_for("dashboard"))
    if not book or book["available_copies"] <= 0:
        flash("Book is not available.")
        return redirect(url_for("dashboard"))

    already = db.execute("""
        SELECT COUNT(*) AS c FROM issues
        WHERE book_id=? AND student_id=? AND return_date IS NULL
    """, (book_id, student["id"])).fetchone()["c"]

    if already:
        flash("This student already has this book.")
        return redirect(url_for("dashboard"))

    issue_date = date.today()
    due_date = issue_date + timedelta(days=DUE_DAYS)
    db.execute("""
        INSERT INTO issues(book_id,student_id,issue_date,due_date)
        VALUES(?,?,?,?)
    """, (book_id, student["id"], issue_date.isoformat(), due_date.isoformat()))
    db.execute(
        "UPDATE books SET available_copies=available_copies-1 WHERE id=?",
        (book_id,)
    )
    db.commit()
    flash(f"Book issued. Due date: {due_date.isoformat()}")
    return redirect(url_for("dashboard"))

@app.route("/return/<int:issue_id>", methods=["POST"])
@login_required()
def return_book(issue_id):
    db = get_db()
    issue = db.execute(
        "SELECT * FROM issues WHERE id=?", (issue_id,)
    ).fetchone()

    if not issue or issue["return_date"]:
        flash("Invalid issue record.")
        return redirect(url_for("dashboard"))

    if session["role"] == "student" and issue["student_id"] != session["user_id"]:
        flash("You can only return your own books.")
        return redirect(url_for("dashboard"))

    return_date = date.today()
    due_date = date.fromisoformat(issue["due_date"])
    late_days = max(0, (return_date - due_date).days)
    fine = late_days * 5

    db.execute("""
        UPDATE issues SET return_date=?, fine=? WHERE id=?
    """, (return_date.isoformat(), fine, issue_id))
    db.execute(
        "UPDATE books SET available_copies=available_copies+1 WHERE id=?",
        (issue["book_id"],)
    )
    db.commit()
    flash(f"Book returned. Fine: ₹{fine}")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
