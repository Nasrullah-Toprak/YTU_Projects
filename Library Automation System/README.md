# 📚 Library Automation System (Kütüphane Otomasyonu)

### 🎓 Course: BLM1031 - Structural Programming (Yapısal Programlama)
### 🧑‍💻 Project Type: Term Project

---

## 📖 Project Overview

This project implements a **Library Automation System** that mimics the logic of relational databases using **C programming**, **CSV-based file storage**, and **linked list data structures**.  
All data (authors, books, students, borrow records, etc.) are stored persistently in CSV files while being dynamically managed in memory through **singly and doubly linked lists**.

---

## ⚙️ Functional Requirements

### 👩‍🏫 Author Operations
- Add / Delete / Update / List authors  
- Each author has a unique auto-incremented `authorID`  
- Data is stored in `Yazarlar.csv` using a **singly linked list**  
- List is sorted by `authorID`

### 🎓 Student Operations
- Add / Delete / Update / List students  
- Each student has: Name, Surname, 8-digit Student Number, and Library Points (initially 100)  
- Managed using a **doubly linked list**  
- Data stored in `Ogrenciler.csv`  

### 📚 Book Operations
- Add / Delete / Update / List books  
- Each book has: Name, 13-digit ISBN, and number of copies  
- Each copy has a unique **tag number** (`ISBN_1`, `ISBN_2`, etc.) and **status** (“RAFTA” or Borrower ID)  
- Data stored in `Kitaplar.csv` and `KitapOrnekleri.csv`  
- Implemented using **singly linked lists**  

### ✍️ Book–Author Relationship
- One book may have multiple authors and vice versa  
- Relationships stored in `KitapYazar.csv`  
- Managed with **dynamic struct arrays** created using file line count  

### 📘 Borrowing and Returning Books
- A student can borrow multiple books  
- Each borrowing record includes: `StudentID`, `BookTag`, `OperationType`, and `Date`  
- Operation types:  
  - `0` → Borrow  
  - `1` → Return  
- Data stored in `OduncIslemleri.csv`  
- Late returns (after 15 days) result in a **–10 penalty points**  
- Students with negative points cannot borrow books  

---

## 🧩 Program Menus

### 🧑‍🎓 Student Menu
1. Add / Delete / Update Student  
2. Display Student Info (by ID or Name)  
3. List Students with Unreturned Books  
4. List Penalized Students  
5. List All Students  
6. Borrow / Return Books  

### 📖 Book Menu
7. Add / Delete / Update Books  
8. Display Book Info and Copies  
9. List Books on Shelf  
10. List Overdue Books  
11. Assign Authors to Books  
12. Update Book’s Author  

### ✍️ Author Menu
13. Add / Delete / Update Authors  
14. Display Author Info and Their Books  

---

## 📁 File Structure

| File Name | Description |
|------------|-------------|
| `main.c` | Entry point and main menu control; Functions for author, student, and book management in addition to book–author relationships |
| `Yazarlar.csv` | Stores all author records |
| `Ogrenciler.csv` | Stores student records |
| `Kitaplar.csv` | Stores main book records |
| `KitapOrnekleri.csv` | Stores each copy of books related to Kitaplar.csv |
| `KitapYazar.csv` | Book–author relationships |
| `OduncIslemleri.csv` | Borrow-return transaction log |

---
