"""
Library Management System
A comprehensive system for managing books, members, and transactions
This could be split into: models.py, database.py, validation.py, reports.py, ui.py, main.py
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
from collections import defaultdict


# ==================== DATA MODELS ====================
# (Could be models.py)

class Book:
    """Represents a book in the library"""
    
    def __init__(self, book_id: str, title: str, author: str, isbn: str, 
                 genre: str, publication_year: int, copies: int = 1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.publication_year = publication_year
        self.total_copies = copies
        self.available_copies = copies
        
    def to_dict(self) -> Dict:
        """Convert book to dictionary"""
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        """Create book from dictionary"""
        book = cls(
            data['book_id'],
            data['title'],
            data['author'],
            data['isbn'],
            data['genre'],
            data['publication_year'],
            data['total_copies']
        )
        book.available_copies = data['available_copies']
        return book
    
    def __str__(self) -> str:
        return f"{self.title} by {self.author} ({self.publication_year}) - {self.available_copies}/{self.total_copies} available"


class Member:
    """Represents a library member"""
    
    def __init__(self, member_id: str, name: str, email: str, phone: str, 
                 join_date: Optional[str] = None):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.join_date = join_date or datetime.now().strftime('%Y-%m-%d')
        self.borrowed_books: List[str] = []
        self.is_active = True
        self.fines = 0.0
        
    def to_dict(self) -> Dict:
        """Convert member to dictionary"""
        return {
            'member_id': self.member_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'join_date': self.join_date,
            'borrowed_books': self.borrowed_books,
            'is_active': self.is_active,
            'fines': self.fines
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Member':
        """Create member from dictionary"""
        member = cls(
            data['member_id'],
            data['name'],
            data['email'],
            data['phone'],
            data['join_date']
        )
        member.borrowed_books = data.get('borrowed_books', [])
        member.is_active = data.get('is_active', True)
        member.fines = data.get('fines', 0.0)
        return member
    
    def __str__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} (ID: {self.member_id}) - {status} - Books: {len(self.borrowed_books)}"


class Transaction:
    """Represents a book borrowing/return transaction"""
    
    def __init__(self, transaction_id: str, member_id: str, book_id: str,
                 transaction_type: str, transaction_date: Optional[str] = None,
                 due_date: Optional[str] = None, return_date: Optional[str] = None):
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.book_id = book_id
        self.transaction_type = transaction_type  # 'borrow' or 'return'
        self.transaction_date = transaction_date or datetime.now().strftime('%Y-%m-%d')
        self.due_date = due_date
        self.return_date = return_date
        
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date,
            'due_date': self.due_date,
            'return_date': self.return_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Create transaction from dictionary"""
        return cls(
            data['transaction_id'],
            data['member_id'],
            data['book_id'],
            data['transaction_type'],
            data['transaction_date'],
            data.get('due_date'),
            data.get('return_date')
        )


# ==================== VALIDATION UTILITIES ====================
# (Could be validation.py)

class Validator:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return re.match(pattern, cleaned) is not None
    
    @staticmethod
    def validate_isbn(isbn: str) -> bool:
        """Validate ISBN format (ISBN-10 or ISBN-13)"""
        cleaned = isbn.replace('-', '').replace(' ', '')
        return len(cleaned) in [10, 13] and cleaned.isdigit()
    
    @staticmethod
    def validate_year(year: int) -> bool:
        """Validate publication year"""
        current_year = datetime.now().year
        return 1000 <= year <= current_year


# ==================== DATABASE MANAGER ====================
# (Could be database.py)

class DatabaseManager:
    """Manages data persistence using JSON files"""
    
    def __init__(self, data_dir: str = 'library_data'):
        self.data_dir = data_dir
        self.books_file = os.path.join(data_dir, 'books.json')
        self.members_file = os.path.join(data_dir, 'members.json')
        self.transactions_file = os.path.join(data_dir, 'transactions.json')
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def save_books(self, books: List[Book]):
        """Save books to JSON file"""
        with open(self.books_file, 'w') as f:
            json.dump([book.to_dict() for book in books], f, indent=2)
            
    def load_books(self) -> List[Book]:
        """Load books from JSON file"""
        if not os.path.exists(self.books_file):
            return []
        with open(self.books_file, 'r') as f:
            data = json.load(f)
            return [Book.from_dict(item) for item in data]
            
    def save_members(self, members: List[Member]):
        """Save members to JSON file"""
        with open(self.members_file, 'w') as f:
            json.dump([member.to_dict() for member in members], f, indent=2)
            
    def load_members(self) -> List[Member]:
        """Load members from JSON file"""
        if not os.path.exists(self.members_file):
            return []
        with open(self.members_file, 'r') as f:
            data = json.load(f)
            return [Member.from_dict(item) for item in data]
            
    def save_transactions(self, transactions: List[Transaction]):
        """Save transactions to JSON file"""
        with open(self.transactions_file, 'w') as f:
            json.dump([txn.to_dict() for txn in transactions], f, indent=2)
            
    def load_transactions(self) -> List[Transaction]:
        """Load transactions from JSON file"""
        if not os.path.exists(self.transactions_file):
            return []
        with open(self.transactions_file, 'r') as f:
            data = json.load(f)
            return [Transaction.from_dict(item) for item in data]


# ==================== LIBRARY MANAGEMENT SYSTEM ====================
# (Could be library_manager.py)

class LibraryManager:
    """Main library management system"""
    
    LOAN_PERIOD_DAYS = 14
    FINE_PER_DAY = 0.50
    MAX_BOOKS_PER_MEMBER = 5
    
    def __init__(self, data_dir: str = 'library_data'):
        self.db = DatabaseManager(data_dir)
        self.books: List[Book] = self.db.load_books()
        self.members: List[Member] = self.db.load_members()
        self.transactions: List[Transaction] = self.db.load_transactions()
        self.validator = Validator()
        
    def save_all(self):
        """Save all data to disk"""
        self.db.save_books(self.books)
        self.db.save_members(self.members)
        self.db.save_transactions(self.transactions)
        
    # ==================== BOOK OPERATIONS ====================
    
    def add_book(self, title: str, author: str, isbn: str, genre: str, 
                 year: int, copies: int = 1) -> Tuple[bool, str]:
        """Add a new book to the library"""
        if not self.validator.validate_isbn(isbn):
            return False, "Invalid ISBN format"
        
        if not self.validator.validate_year(year):
            return False, "Invalid publication year"
            
        # Check for duplicate ISBN
        for book in self.books:
            if book.isbn == isbn:
                return False, "Book with this ISBN already exists"
        
        book_id = f"B{len(self.books) + 1:04d}"
        book = Book(book_id, title, author, isbn, genre, year, copies)
        self.books.append(book)
        self.save_all()
        return True, f"Book added successfully with ID: {book_id}"
    
    def search_books(self, query: str, search_by: str = 'title') -> List[Book]:
        """Search books by title, author, or genre"""
        query = query.lower()
        results = []
        
        for book in self.books:
            if search_by == 'title' and query in book.title.lower():
                results.append(book)
            elif search_by == 'author' and query in book.author.lower():
                results.append(book)
            elif search_by == 'genre' and query in book.genre.lower():
                results.append(book)
            elif search_by == 'isbn' and query in book.isbn:
                results.append(book)
                
        return results
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get book by ID"""
        for book in self.books:
            if book.book_id == book_id:
                return book
        return None
    
    def update_book_copies(self, book_id: str, new_total: int) -> Tuple[bool, str]:
        """Update total number of copies for a book"""
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found"
            
        borrowed = book.total_copies - book.available_copies
        if new_total < borrowed:
            return False, f"Cannot reduce copies below borrowed count ({borrowed})"
            
        book.total_copies = new_total
        book.available_copies = new_total - borrowed
        self.save_all()
        return True, "Book copies updated successfully"
    
    def delete_book(self, book_id: str) -> Tuple[bool, str]:
        """Delete a book from the library"""
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found"
            
        if book.available_copies < book.total_copies:
            return False, "Cannot delete book with active loans"
            
        self.books.remove(book)
        self.save_all()
        return True, "Book deleted successfully"
    
    # ==================== MEMBER OPERATIONS ====================
    
    def add_member(self, name: str, email: str, phone: str) -> Tuple[bool, str]:
        """Add a new member to the library"""
        if not self.validator.validate_email(email):
            return False, "Invalid email format"
            
        if not self.validator.validate_phone(phone):
            return False, "Invalid phone number format"
            
        # Check for duplicate email
        for member in self.members:
            if member.email == email:
                return False, "Member with this email already exists"
        
        member_id = f"M{len(self.members) + 1:04d}"
        member = Member(member_id, name, email, phone)
        self.members.append(member)
        self.save_all()
        return True, f"Member added successfully with ID: {member_id}"
    
    def search_members(self, query: str, search_by: str = 'name') -> List[Member]:
        """Search members by name, email, or ID"""
        query = query.lower()
        results = []
        
        for member in self.members:
            if search_by == 'name' and query in member.name.lower():
                results.append(member)
            elif search_by == 'email' and query in member.email.lower():
                results.append(member)
            elif search_by == 'id' and query in member.member_id.lower():
                results.append(member)
                
        return results
    
    def get_member_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None
    
    def deactivate_member(self, member_id: str) -> Tuple[bool, str]:
        """Deactivate a member account"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Member not found"
            
        if len(member.borrowed_books) > 0:
            return False, "Cannot deactivate member with borrowed books"
            
        if member.fines > 0:
            return False, f"Member has outstanding fines: ${member.fines:.2f}"
            
        member.is_active = False
        self.save_all()
        return True, "Member deactivated successfully"
    
    def activate_member(self, member_id: str) -> Tuple[bool, str]:
        """Activate a member account"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Member not found"
            
        member.is_active = True
        self.save_all()
        return True, "Member activated successfully"
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def borrow_book(self, member_id: str, book_id: str) -> Tuple[bool, str]:
        """Process a book borrowing transaction"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Member not found"
            
        if not member.is_active:
            return False, "Member account is inactive"
            
        if member.fines > 0:
            return False, f"Member has outstanding fines: ${member.fines:.2f}"
            
        if len(member.borrowed_books) >= self.MAX_BOOKS_PER_MEMBER:
            return False, f"Member has reached maximum book limit ({self.MAX_BOOKS_PER_MEMBER})"
            
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found"
            
        if book.available_copies <= 0:
            return False, "No copies available"
            
        # Create transaction
        transaction_id = f"T{len(self.transactions) + 1:06d}"
        transaction_date = datetime.now()
        due_date = transaction_date + timedelta(days=self.LOAN_PERIOD_DAYS)
        
        transaction = Transaction(
            transaction_id,
            member_id,
            book_id,
            'borrow',
            transaction_date.strftime('%Y-%m-%d'),
            due_date.strftime('%Y-%m-%d')
        )
        
        # Update records
        book.available_copies -= 1
        member.borrowed_books.append(book_id)
        self.transactions.append(transaction)
        self.save_all()
        
        return True, f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}"
    
    def return_book(self, member_id: str, book_id: str) -> Tuple[bool, str]:
        """Process a book return transaction"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Member not found"
            
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Book not found"
            
        if book_id not in member.borrowed_books:
            return False, "Member has not borrowed this book"
            
        # Find the borrow transaction
        borrow_transaction = None
        for txn in reversed(self.transactions):
            if (txn.member_id == member_id and txn.book_id == book_id and 
                txn.transaction_type == 'borrow' and txn.return_date is None):
                borrow_transaction = txn
                break
                
        if not borrow_transaction:
            return False, "No active loan found for this book"
            
        # Calculate fine if overdue
        return_date = datetime.now()
        due_date = datetime.strptime(borrow_transaction.due_date, '%Y-%m-%d')
        fine = 0.0
        
        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = days_overdue * self.FINE_PER_DAY
            member.fines += fine
            
        # Create return transaction
        transaction_id = f"T{len(self.transactions) + 1:06d}"
        return_transaction = Transaction(
            transaction_id,
            member_id,
            book_id,
            'return',
            return_date.strftime('%Y-%m-%d')
        )
        
        # Update records
        borrow_transaction.return_date = return_date.strftime('%Y-%m-%d')
        book.available_copies += 1
        member.borrowed_books.remove(book_id)
        self.transactions.append(return_transaction)
        self.save_all()
        
        message = "Book returned successfully"
        if fine > 0:
            message += f". Fine charged: ${fine:.2f}"
        return True, message
    
    def pay_fine(self, member_id: str, amount: float) -> Tuple[bool, str]:
        """Process a fine payment"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Member not found"
            
        if amount <= 0:
            return False, "Payment amount must be positive"
            
        if amount > member.fines:
            return False, f"Payment exceeds fine amount (${member.fines:.2f})"
            
        member.fines -= amount
        self.save_all()
        
        remaining = member.fines
        message = f"Payment of ${amount:.2f} processed successfully"
        if remaining > 0:
            message += f". Remaining balance: ${remaining:.2f}"
        return True, message
    
    # ==================== REPORTING ====================
    
    def get_overdue_books(self) -> List[Dict]:
        """Get list of overdue books"""
        overdue = []
        today = datetime.now()
        
        for txn in self.transactions:
            if txn.transaction_type == 'borrow' and txn.return_date is None:
                due_date = datetime.strptime(txn.due_date, '%Y-%m-%d')
                if today > due_date:
                    member = self.get_member_by_id(txn.member_id)
                    book = self.get_book_by_id(txn.book_id)
                    days_overdue = (today - due_date).days
                    
                    overdue.append({
                        'member_name': member.name if member else 'Unknown',
                        'member_id': txn.member_id,
                        'book_title': book.title if book else 'Unknown',
                        'book_id': txn.book_id,
                        'due_date': txn.due_date,
                        'days_overdue': days_overdue,
                        'fine': days_overdue * self.FINE_PER_DAY
                    })
                    
        return sorted(overdue, key=lambda x: x['days_overdue'], reverse=True)
    
    def get_popular_books(self, limit: int = 10) -> List[Dict]:
        """Get most borrowed books"""
        borrow_count = defaultdict(int)
        
        for txn in self.transactions:
            if txn.transaction_type == 'borrow':
                borrow_count[txn.book_id] += 1
                
        popular = []
        for book_id, count in borrow_count.items():
            book = self.get_book_by_id(book_id)
            if book:
                popular.append({
                    'book_id': book_id,
                    'title': book.title,
                    'author': book.author,
                    'borrow_count': count
                })
                
        return sorted(popular, key=lambda x: x['borrow_count'], reverse=True)[:limit]
    
    def get_member_history(self, member_id: str) -> List[Dict]:
        """Get borrowing history for a member"""
        history = []
        
        for txn in self.transactions:
            if txn.member_id == member_id and txn.transaction_type == 'borrow':
                book = self.get_book_by_id(txn.book_id)
                history.append({
                    'transaction_id': txn.transaction_id,
                    'book_title': book.title if book else 'Unknown',
                    'book_id': txn.book_id,
                    'borrow_date': txn.transaction_date,
                    'due_date': txn.due_date,
                    'return_date': txn.return_date or 'Not returned',
                    'status': 'Returned' if txn.return_date else 'Borrowed'
                })
                
        return sorted(history, key=lambda x: x['borrow_date'], reverse=True)
    
    def get_statistics(self) -> Dict:
        """Get library statistics"""
        total_books = sum(book.total_copies for book in self.books)
        available_books = sum(book.available_copies for book in self.books)
        borrowed_books = total_books - available_books
        
        active_members = sum(1 for m in self.members if m.is_active)
        inactive_members = len(self.members) - active_members
        
        total_fines = sum(m.fines for m in self.members)
        
        overdue_count = len(self.get_overdue_books())
        
        return {
            'total_book_titles': len(self.books),
            'total_book_copies': total_books,
            'available_copies': available_books,
            'borrowed_copies': borrowed_books,
            'total_members': len(self.members),
            'active_members': active_members,
            'inactive_members': inactive_members,
            'total_transactions': len(self.transactions),
            'overdue_books': overdue_count,
            'total_outstanding_fines': total_fines
        }


# ==================== COMMAND LINE INTERFACE ====================
# (Could be cli.py or ui.py)

class LibraryCLI:
    """Command line interface for the library system"""
    
    def __init__(self):
        self.library = LibraryManager()
        self.running = True
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60 + "\n")
        
    def print_menu(self, title: str, options: List[str]):
        """Print a menu"""
        self.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print(f"  {len(options) + 1}. Back")
        print()
        
    def get_input(self, prompt: str) -> str:
        """Get user input"""
        return input(f"  {prompt}: ").strip()
        
    def pause(self):
        """Pause and wait for user"""
        input("\n  Press Enter to continue...")
        
    # ==================== MENU HANDLERS ====================
    
    def main_menu(self):
        """Display main menu"""
        while self.running:
            options = [
                "Book Management",
                "Member Management",
                "Transactions",
                "Reports",
                "Exit"
            ]
            self.print_menu("Library Management System - Main Menu", options)
            
            choice = self.get_input("Select option")
            
            if choice == '1':
                self.book_menu()
            elif choice == '2':
                self.member_menu()
            elif choice == '3':
                self.transaction_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '5':
                print("\n  Thank you for using the Library Management System!\n")
                self.running = False
            else:
                print("\n  Invalid option. Please try again.")
                self.pause()
                
    def book_menu(self):
        """Book management menu"""
        while True:
            options = [
                "Add New Book",
                "Search Books",
                "View All Books",
                "Update Book Copies",
                "Delete Book"
            ]
            self.print_menu("Book Management", options)
            
            choice = self.get_input("Select option")
            
            if choice == '1':
                self.add_book_ui()
            elif choice == '2':
                self.search_books_ui()
            elif choice == '3':
                self.view_all_books()
            elif choice == '4':
                self.update_book_copies_ui()
            elif choice == '5':
                self.delete_book_ui()
            elif choice == '6':
                break
            else:
                print("\n  Invalid option. Please try again.")
                self.pause()
                
    def member_menu(self):
        """Member management menu"""
        while True:
            options = [
                "Add New Member",
                "Search Members",
                "View All Members",
                "View Member History",
                "Deactivate Member",
                "Activate Member"
            ]
            self.print_menu("Member Management", options)
            
            choice = self.get_input("Select option")
            
            if choice == '1':
                self.add_member_ui()
            elif choice == '2':
                self.search_members_ui()
            elif choice == '3':
                self.view_all_members()
            elif choice == '4':
                self.view_member_history_ui()
            elif choice == '5':
                self.deactivate_member_ui()
            elif choice == '6':
                self.activate_member_ui()
            elif choice == '7':
                break
            else:
                print("\n  Invalid option. Please try again.")
                self.pause()
                
    def transaction_menu(self):
        """Transaction menu"""
        while True:
            options = [
                "Borrow Book",
                "Return Book",
                "Pay Fine"
            ]
            self.print_menu("Transactions", options)
            
            choice = self.get_input("Select option")
            
            if choice == '1':
                self.borrow_book_ui()
            elif choice == '2':
                self.return_book_ui()
            elif choice == '3':
                self.pay_fine_ui()
            elif choice == '4':
                break
            else:
                print("\n  Invalid option. Please try again.")
                self.pause()
                
    def reports_menu(self):
        """Reports menu"""
        while True:
            options = [
                "Overdue Books",
                "Popular Books",
                "Library Statistics"
            ]
            self.print_menu("Reports", options)
            
            choice = self.get_input("Select option")
            
            if choice == '1':
                self.show_overdue_books()
            elif choice == '2':
                self.show_popular_books()
            elif choice == '3':
                self.show_statistics()
            elif choice == '4':
                break
            else:
                print("\n  Invalid option. Please try again.")
                self.pause()
    
    # ==================== UI IMPLEMENTATIONS ====================
    
    def add_book_ui(self):
        """UI for adding a book"""
        self.print_header("Add New Book")
        
        title = self.get_input("Title")
        author = self.get_input("Author")
        isbn = self.get_input("ISBN")
        genre = self.get_input("Genre")
        year = self.get_input("Publication Year")
        copies = self.get_input("Number of Copies")
        
        try:
            year = int(year)
            copies = int(copies)
            success, message = self.library.add_book(title, author, isbn, genre, year