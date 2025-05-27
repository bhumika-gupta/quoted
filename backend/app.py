from flask import Flask, request, jsonify
from main import get_quotes_for_book # imports scraping logic
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # allows React to connect

@app.route('/api/search')
def search_quotes():
    book_name = request.args.get('book_name')
    if not book_name:
        return jsonify({"error": "Book name is required"}), 400

    try:
        quotes = get_quotes_for_book(book_name)
        if not quotes:
            return jsonify({"message": "No quotes found for this book"}), 404
        return jsonify({"quotes": quotes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)