# Library Management System

A Python Flask + SQLite web application based on the given Library Management System problem statement.

## Technology Stack
- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2 templates

## Features
1. Separate librarian and student logins
2. Librarian can add, edit and delete books
3. Book details: title, author, category and number of copies
4. Issue books to students
5. Automatic 14-day due date
6. Return books
7. Automatic late fine calculation: ₹5 per late day
8. Search by title, author or category
9. Check available copies
10. Student dashboard with issued books and due dates
11. SQLite database for persistent data

## Default Login Details
Librarian:
- Username: librarian
- Password: admin123

Student:
- Username: student1
- Password: student123

Another student:
- Username: student2
- Password: student123

## How to Run

### 1. Open the project folder in VS Code

### 2. Create/activate a virtual environment (optional)
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Flask
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
```bash
python database.py
```

### 5. Start the application
```bash
python app.py
```

### 6. Open in browser
Go to:
http://127.0.0.1:5000

The `library.db` file is automatically created in the project folder.

## Project Structure

Library_Management_System/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── librarian_dashboard.html
│   ├── student_dashboard.html
│   ├── book_form.html
│   └── search.html
└── static/
    └── style.css

## Problem Statement Mapping

- Separate logins → users table + role-based access
- Add/edit/delete books → librarian dashboard
- Issue/return → issues table and issue/return routes
- Due dates → automatically set to 14 days
- Fines → ₹5 per late day
- Search → title/author/category search
- Availability → available_copies
- Student dashboard → currently issued books and due dates
