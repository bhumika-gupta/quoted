from flask import Flask, request, jsonify
from flask_cors import CORS
from main import get_quotes_for_book # imports scraping logic


app = Flask(__name__)
# CORS(app) # allows React to connect
# Allow only localhost:5173 (React dev server)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins
CORS(app, resources={r"/*": {"origins": "http://localhost:5174"}})


@app.route('/api/search')
def search_quotes():
    book = request.args.get('book')
    if not book:
        return jsonify({"error": "Book name is required"}), 400

    try:
        quotes = get_quotes_for_book(book)
        if not quotes:
            return jsonify({"message": "No quotes found for this book"}), 404
        return jsonify({"quotes": quotes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    print("Test endpoint hit")
    return jsonify({"message": "Backend is working!"})

if __name__ == '__main__':
    app.run(debug=True, port=5050)