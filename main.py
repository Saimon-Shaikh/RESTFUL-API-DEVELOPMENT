from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Mock Database (In-Memory List of Dictionaries) ---
# NOTE: In a production environment, this would be replaced by a database connection (e.g., SQLAlchemy/SQLite).
BOOK_DATA = [
    {"id": 1, "title": "The Name of the Wind", "author": "Patrick Rothfuss", "isbn": "9780756404741", "publication_year": 2007, "quantity": 5},
    {"id": 2, "title": "A Memory of Light", "author": "Robert Jordan", "isbn": "9780765325950", "publication_year": 2013, "quantity": 10},
]
# ID counter for new books
next_book_id = 3 

# --- Helper function to find a book by ID ---
def find_book(book_id):
    """Searches BOOK_DATA for a book with the given ID."""
    for book in BOOK_DATA:
        if book['id'] == book_id:
            return book
    return None

# --- R (Read All) ---
@app.route('/api/books', methods=['GET'])
def get_all_books():
    """
    Retrieves a list of all books in the inventory.
    Returns: JSON array of books.
    """
    # Returns 200 OK by default
    return jsonify(BOOK_DATA)

# --- C (Create) ---
@app.route('/api/books', methods=['POST'])
def add_book():
    """
    Adds a new book to the inventory.
    Requires JSON input with 'title' and 'author'.
    """
    new_book = request.get_json()
    
    # 1. Input Validation: Check for required fields
    if not new_book or 'title' not in new_book or 'author' not in new_book:
        # Returns 400 Bad Request
        return jsonify({"message": "Invalid book data provided. 'title' and 'author' are required."}), 400

    global next_book_id
    
    # 2. Assign properties and set defaults if missing
    new_book['id'] = next_book_id
    new_book['isbn'] = new_book.get('isbn', 'N/A')
    new_book['publication_year'] = new_book.get('publication_year', None)
    new_book['quantity'] = new_book.get('quantity', 1) 
    
    # 3. Add to the mock database
    BOOK_DATA.append(new_book)
    next_book_id += 1
    
    # Returns 201 Created and the new resource
    return jsonify(new_book), 201 

# --- R (Read Single Book) ---
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
    Retrieves details for a specific book by its ID.
    """
    book = find_book(book_id)
    
    if book is None:
        # Returns 404 Not Found
        return jsonify({"message": f"Book with id {book_id} not found."}), 404
        
    return jsonify(book)

# --- U (Update) ---
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Updates all details for a specific book by its ID.
    Requires JSON input containing the fields to update.
    """
    book_to_update = find_book(book_id)
    
    if book_to_update is None:
        # Returns 404 Not Found
        return jsonify({"message": f"Book with id {book_id} not found."}), 404

    update_data = request.get_json()
    
    # Update properties of the book object in place
    if 'title' in update_data:
        book_to_update['title'] = update_data['title']
    if 'author' in update_data:
        book_to_update['author'] = update_data['author']
    if 'isbn' in update_data:
        book_to_update['isbn'] = update_data['isbn']
    if 'publication_year' in update_data:
        book_to_update['publication_year'] = update_data['publication_year']
    if 'quantity' in update_data:
        book_to_update['quantity'] = update_data['quantity']

    # Returns 200 OK and the updated resource
    return jsonify(book_to_update)

# --- D (Delete) ---
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Removes a book from the inventory by its ID.
    """
    global BOOK_DATA
    original_length = len(BOOK_DATA)
    
    # Filter out the book with the matching ID
    BOOK_DATA = [book for book in BOOK_DATA if book['id'] != book_id]
    
    if len(BOOK_DATA) == original_length:
        # If the length hasn't changed, the book was not found
        # Returns 404 Not Found
        return jsonify({"message": f"Book with id {book_id} not found."}), 404
    
    # Returns 204 No Content (Standard response for successful deletion)
    return '', 204 

if __name__ == '__main__':
    # Run the application in debug mode on the standard port 5000
    app.run(debug=True)
