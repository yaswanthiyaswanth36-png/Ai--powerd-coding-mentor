# Library Management System - Project Documentation

## 1. Project Title
Library Management System

## 2. Problem Statement
Build a Library Management System where librarians can add and manage books, issue and return books to students, track due dates and calculate fines automatically, while students can search the catalogue and check availability.

## 3. Project Overview
The system is a web-based library application developed using Python Flask and SQLite. It provides separate access for librarians and students. Librarians manage books and circulation, while students search the catalogue and view their issued books.

## 4. Objectives
- Digitize library book management.
- Maintain accurate book availability.
- Simplify issuing and returning books.
- Automatically calculate due dates and late fines.
- Provide role-based dashboards.
- Allow students to search books quickly.

## 5. Scope
The project covers book management, user login, issue/return transactions, due-date tracking, fine calculation, search, and availability checking.

## 6. Modules
### Authentication Module
Handles librarian/student login and role-based access.

### Book Management Module
Allows librarians to add, edit and delete books.

### Issue Module
Allows librarians to issue available books to students and automatically assign a 14-day due date.

### Return Module
Records returned books, updates available copies and calculates fines.

### Search Module
Students and librarians can search books by title, author or category.

### Student Dashboard
Shows currently issued books, issue dates and due dates.

## 7. Database Tables

### users
- id
- username
- password
- role

### books
- id
- title
- author
- category
- total_copies
- available_copies

### issues
- id
- book_id
- student_id
- issue_date
- due_date
- return_date
- fine

## 8. Fine Calculation
Fine = Number of late days × ₹5.

Example:
If a book is returned 3 days late:
Fine = 3 × ₹5 = ₹15.

## 9. Future Enhancements
- Password hashing
- Admin user creation
- Email/SMS due-date reminders
- PDF reports
- Fine payment tracking
- Book cover images
- Barcode/QR code support
- Advanced analytics
