from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

# --- 1. Initialization and Configuration ---
app = Flask(__name__)

# Configure SQLAlchemy to use a SQLite database file named 'library.db'
# This file will be created in the current directory.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
# Recommended setting to silence a warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)

# --- 2. Database Model Definition (The Python Class for the 'book' table) ---
class Book(db.Model):
    """
    Defines the structure of the 'book' table in the database.
    This class represents the Book resource in our API.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True) # Unique, optional ISBN
    publication_year = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        """Converts the Book object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "quantity": self.quantity,
        }
    
    def __repr__(self):
        return f'<Book {self.title}>'

# --- 3. CRUD Endpoints (Using SQLAlchemy) ---

# --- R (Read All) and C (Create) ---
@app.route('/api/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        # C (Create) - Add a new book
        data = request.get_json()
        
        # Basic Validation
        if not data or 'title' not in data or 'author' not in data:
            return jsonify({"message": "Invalid data. 'title' and 'author' are required."}), 400

        try:
            # Create a new Book instance from the request data
            new_book = Book(
                title=data['title'],
                author=data['author'],
                # Use .get() for optional fields
                isbn=data.get('isbn'), 
                publication_year=data.get('publication_year'),
                quantity=data.get('quantity', 1)
            )
            
            db.session.add(new_book)
            db.session.commit() # Save the new record to the database
            
            # Returns 201 Created
            return jsonify(new_book.to_dict()), 201
            
        except Exception as e:
            # Rollback the session if an error occurs (e.g., non-unique ISBN)
            db.session.rollback() 
            # In a real app, log the error 'e'
            return jsonify({"message": "Error creating book.", "error": str(e)}), 500

    # R (Read All) - Retrieve all books
    elif request.method == 'GET':
        # Query all records from the 'book' table
        books = Book.query.all()
        # Convert list of Book objects to list of dictionaries for JSON serialization
        return jsonify([book.to_dict() for book in books])

# --- R (Read Single), U (Update), and D (Delete) ---
@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
def book_detail(book_id):
    # R (Read Single) - Find the book by primary key (ID)
    book = Book.query.get(book_id)
    
    if book is None:
        # Returns 404 Not Found
        return jsonify({"message": f"Book with id {book_id} not found."}), 404

    if request.method == 'GET':
        return jsonify(book.to_dict())

    elif request.method == 'PUT':
        # U (Update)
        data = request.get_json()
        
        # Update fields only if they are provided in the request body
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'isbn' in data:
            book.isbn = data['isbn']
        if 'publication_year' in data:
            book.publication_year = data['publication_year']
        if 'quantity' in data:
            book.quantity = data['quantity']
        
        db.session.commit() # Save changes to the database
        # Returns 200 OK
        return jsonify(book.to_dict())

    elif request.method == 'DELETE':
        # D (Delete)
        db.session.delete(book)
        db.session.commit() # Execute the deletion
        
        # Returns 204 No Content (Standard response for successful deletion)
        return '', 204

# --- 4. Application Runner and Database Setup ---
if __name__ == '__main__':
    # Creates the application context required for database operations
    with app.app_context():
        # Creates the database tables defined by the 'Book' model if they don't exist
        db.create_all() 
        print("Database tables created/checked.")
        
        # Optional: Add initial mock data if the database is empty
        if not Book.query.first():
            print("Adding initial mock data...")
            initial_books = [
                Book(title="The Name of the Wind", author="Patrick Rothfuss", isbn="9780756404741", publication_year=2007, quantity=5),
                Book(title="A Memory of Light", author="Robert Jordan", isbn="9780765325950", publication_year=2013, quantity=10),
            ]
            db.session.add_all(initial_books)
            db.session.commit()
            print("Mock data added.")
            
    # Run the application
    app.run(debug=True)
