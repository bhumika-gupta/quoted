from flask import Flask, request, jsonify
from flask_cors import CORS
from main import get_search_results
from main import get_quotes_page_url
from main import extract_quotes
from main import get_quotes_for_book # imports scraping logic


app = Flask(__name__)
# CORS(app) # allows React to connect
# Allow only localhost:5173 (React dev server)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

@app.route('/api/search_results')
def search_quotes():
    userBook = request.args.get('userBook')
    if not userBook:
        return jsonify({"error": "Book name is required"}), 400
    
    try: 
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
        results = get_search_results(userBook, headers)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/quotes')
def quotes():
    href = request.args.get("href") # this comes from frontend
    if not href:
        return jsonify({"error": "Missing book href"}), 400
    
    headers = {"User-Agent": "..."}
    full_url = "https://www.goodreads.com" + href
    quotes_url = get_quotes_page_url(full_url, headers=headers)
    if not quotes_url:
        return jsonify({"error": "Could not find quotes page"}), 404
    quotes = extract_quotes(quotes_url, headers=headers)
    if not quotes:
        return jsonify({"error": "No quotes found."}), 404
    return jsonify({"quotes": quotes})

@app.route('/test')
def test():
    print("Test endpoint hit")
    return jsonify({"message": "Backend is working!"})

if __name__ == '__main__':
    app.run(debug=True, port=5050)