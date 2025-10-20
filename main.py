# Improved Flask RESTful API (single-file)
from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # enable CORS for testing; configure origins in production

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "quantity": self.quantity,
        }

# Error handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"message": "Bad request", "details": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"message": "Internal server error", "details": str(e)}), 500

def parse_json_request():
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"message": "Request body must be JSON"}), 400)
    return data, None

# Create / List with pagination and filtering
@app.route('/api/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        data, err = parse_json_request()
        if err:
            return err
        if 'title' not in data or 'author' not in data:
            return jsonify({"message": "Invalid data. 'title' and 'author' are required."}), 400
        try:
            book = Book(
                title=str(data['title']).strip(),
                author=str(data['author']).strip(),
                isbn=data.get('isbn'),
                publication_year=data.get('publication_year'),
                quantity=int(data.get('quantity', 1))
            )
            db.session.add(book)
            db.session.commit()
            location = url_for('book_detail', book_id=book.id)
            resp = jsonify(book.to_dict())
            resp.status_code = 201
            resp.headers['Location'] = location
            return resp
        except IntegrityError as ie:
            db.session.rollback()
            return jsonify({"message": "Integrity error", "details": "ISBN must be unique."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error creating book", "details": str(e)}), 500

    # GET: list with optional filters + pagination
    query = Book.query
    # filters
    author = request.args.get('author')
    title = request.args.get('title')
    isbn = request.args.get('isbn')
    year = request.args.get('publication_year')
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if isbn:
        query = query.filter(Book.isbn == isbn)
    if year:
        try:
            y = int(year)
            query = query.filter(Book.publication_year == y)
        except ValueError:
            return jsonify({"message": "Invalid publication_year filter"}), 400

    # pagination
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
    except ValueError:
        return jsonify({"message": "Invalid pagination parameters"}), 400

    pag = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [b.to_dict() for b in pag.items]
    return jsonify({
        "items": items,
        "total": pag.total,
        "page": pag.page,
        "per_page": pag.per_page,
        "pages": pag.pages
    })

# Retrieve / Update / Partial update / Delete
@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def book_detail(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"message": f"Book with id {book_id} not found."}), 404

    if request.method == 'GET':
        return jsonify(book.to_dict())

    if request.method == 'PUT':
        # Full replace — require title and author
        data, err = parse_json_request()
        if err:
            return err
        if 'title' not in data or 'author' not in data:
            return jsonify({"message": "PUT requires 'title' and 'author'."}), 400
        try:
            book.title = str(data['title']).strip()
            book.author = str(data['author']).strip()
            book.isbn = data.get('isbn')
            book.publication_year = data.get('publication_year')
            book.quantity = int(data.get('quantity', book.quantity))
            db.session.commit()
            return jsonify(book.to_dict())
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "ISBN must be unique."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating book", "details": str(e)}), 500

    if request.method == 'PATCH':
        # Partial update
        data, err = parse_json_request()
        if err:
            return err
        try:
            if 'title' in data:
                book.title = data['title']
            if 'author' in data:
                book.author = data['author']
            if 'isbn' in data:
                book.isbn = data['isbn']
            if 'publication_year' in data:
                book.publication_year = data['publication_year']
            if 'quantity' in data:
                book.quantity = int(data['quantity'])
            db.session.commit()
            return jsonify(book.to_dict())
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "ISBN must be unique."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating book", "details": str(e)}), 500

    if request.method == 'DELETE':
        try:
            db.session.delete(book)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting book", "details": str(e)}), 500

if __name__ == '__main__':
    # Create DB + seed if empty
    with app.app_context():
        db.create_all()
        if not Book.query.first():
            b1 = Book(title="The Name of the Wind", author="Patrick Rothfuss", isbn="9780756404741", publication_year=2007, quantity=5)
            b2 = Book(title="A Memory of Light", author="Robert Jordan", isbn="9780765325950", publication_year=2013, quantity=10)
            b3 = Book(title="The Martian", author="Andy Weir", isbn="9780804139024", publication_year=2011, quantity=15)
            b4 = Book(title="Project Hail Mary", author="Andy Weir", isbn="9780593136204", publication_year=2021, quantity=8)
            b5 = Book(title="Where the Crawdads Sing", author="Delia Owens", isbn="9780735219090", publication_year=2018, quantity=2)
            b6 = Book(title="Dune", author="Frank Herbert", isbn="9780441172719", publication_year=1965, quantity=20)
            b7 = Book(title="Circe", author="Madeline Miller", isbn="9780316556347", publication_year=2018, quantity=7)
            b8 = Book(title="The Hitchhiker's Guide to the Galaxy", author="Douglas Adams", isbn="9780345391803", publication_year=1979, quantity=12)
            b9 = Book(title="Educated: A Memoir", author="Tara Westover", isbn="9780399592471", publication_year=2018, quantity=4)
            b10 = Book(title="A Game of Thrones", author="George R.R. Martin", isbn="9780553381675", publication_year=1996, quantity=6)

            db.session.add_all([b1, b2, b3, b4, b5, b6, b7, b8, b9, b10])
            db.session.commit()
    app.run(debug=True)