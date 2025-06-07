from flask import Flask, request, jsonify # import flask and necessary modules
from flask_cors import CORS # import CORS to allow cross-origin requests
from main import get_search_results
from main import get_quotes_page_url
from main import extract_quotes
from main import get_quotes_from_href # imports scraping logic


app = Flask(__name__)
# CORS(app) # allows React to connect
# Allow only localhost:5173 (React dev server)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

@app.route('/api/search_results') # define an endpoint to handle search requests
def search_quotes():
    userBook = request.args.get('userBook') # get the book name from the query parameter
    if not userBook:
        return jsonify({"error": "Book name is required"}), 400 # return error if no book name is provided
    
    try: 
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
        results = get_search_results(userBook, headers) # call scraping function to get top 5 search results
        return jsonify({"results": results}) # return results as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # handle unexpected errors
    
@app.route('/api/quotes') # define an endpoint to fetch quotes for a specific book
def quotes():
    href = request.args.get("href") # get the Goodreads link (partial path) from frontend
    if not href:
        return jsonify({"error": "Missing book href"}), 400 # return error if href is not provided
    
    try:
        quotes = get_quotes_from_href(href)
        if "error" in quotes:
            return jsonify(quotes), 404
        if not quotes:
            return jsonify({"error": "No quotes found."}), 404
        return jsonify(quotes)
        # return jsonify({"quotes": quotes})
    except Exception as e:
        print("Internal error:", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test') # a simple route to verify the backend is working
def test():
    print("Test endpoint hit") # logs to backend console
    return jsonify({"message": "Backend is working!"}) # returns a success message

if __name__ == '__main__':
    app.run(debug=True, port=5050) # run the Flask app in debug mode on port 5050