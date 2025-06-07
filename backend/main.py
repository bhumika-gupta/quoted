import httpx # for making HTTP requests
from selectolax.parser import HTMLParser # lightweight HTML parser
# import sys # access command line arguments
import json # for JSON handling

def get_search_results(user_search, headers):
    
    # return a list of 5 results
    # https://www.goodreads.com/search?q=the+subtle+art&qid=
    # https://www.goodreads.com/search?q=atomic&qid=
    # https://www.goodreads.com/search?q=atomic+habits&qid=
    # https://www.goodreads.com/search?q=harry+potter&qid=
    # https://www.goodreads.com/search?q=harry+potter+and+the+sorcerer%27s+stone&qid=

    # constructs the Goodreads search URL using the user's query
    search_result = "https://www.goodreads.com/search?q=" + user_search.replace(" ", "+") + "&qid="
    search_resp = httpx.get(search_result, headers=headers, timeout=10) # sends a GET request to Goodreads
    search_html = HTMLParser(search_resp.text) # parses the HTML response
    
    # selects the first 5 books from the search results
    books = search_html.css("table.tableList tr[itemtype='http://schema.org/Book']")
    results = []
    for book in books[:5]: # limit to top 5 results
        bookTitle = book.css_first("a.bookTitle span[itemprop='name']") # extracts book title
        bookAuthor = book.css_first("span[itemprop='author'] span[itemprop='name']") # extracts author
        publishedYearBox = book.css_first("span.greyText.smallText.uitext") # tries to extract published year text
        
        # extracts the year from the string if available
        if publishedYearBox: # in case it's None
            publishedYearContent = publishedYearBox.text()
            publishedYearText = publishedYearContent.split() # TODO: use regex to find 4 digit year
            publishedYear = publishedYearText[2]
        else:
            publishedYear = "N/A"

        # appends the collected book data to the results list
        results.append({
            "bookTitle": bookTitle.text() if bookTitle else "N/A", 
            "bookAuthor": bookAuthor.text() if bookAuthor else "N/A", 
            "publishedYear": publishedYear,
            "href": book.css_first("a.bookTitle").attributes["href"]})
        
    return results

def get_book_url(book_name, headers):
    # searches Goodreads for the book name and returns the URL of the first result
    search_result = "https://www.goodreads.com/search?q=" + book_name.replace(" ", "+") # TODO: better format into search result
    search_resp = httpx.get(search_result, headers=headers, timeout=10)
    search_html = HTMLParser(search_resp.text)

    first_result = search_html.css_first("a.bookTitle") # gets first book result
    if not first_result:
        return None # print("No book results found.")

    first_result_href = first_result.attributes["href"] # gets the href value
    book_url = "https://www.goodreads.com" + first_result_href # constructs the full URL
    
    return book_url

def get_quotes_page_url(book_url, headers):
    # fetches the book page and finds the link to the quotes page
    book_resp = httpx.get(book_url, headers=headers, timeout=10)
    book_html = HTMLParser(book_resp.text)

    quotes_link = book_html.css_first("a.DiscussionCard") # looks for a quotes page link
    if not quotes_link:
        return None
    
    quotes_url = quotes_link.attributes["href"] # extracts href from the link

    # print("Book page:", book_url) # debugging
    # print("Quotes page:", quotes_url) # debugging

    if not quotes_url:
        return None # print("No quotes link found.")

    return quotes_url

def handle_redirect(resp, headers):
    # follows a redirect if Goodreads returns a page with a single link to the real quotes page
    html = HTMLParser(resp.text)
    redirect_link = html.css_first("a") # gets first link on the page
    
    if redirect_link:
        redirected_url = redirect_link.attributes.get("href", "") # gets the URL
        # checks if the URL is a valid quotes link
        if "quotes" in redirected_url and "goodreads.com" in redirected_url and "blog" not in redirected_url:
            new_resp = httpx.get(redirected_url, headers=headers, timeout=15) # print("Redirecting to actual quotes page:", redirected_url)
            return new_resp
    return resp # returns original response if no redirect was followed

def extract_quotes(quotes_url, headers, max_pages=100):
    # fetches quotes from the quotes page and paginates if there are multiple pages
    quotes_resp = httpx.get(quotes_url, headers=headers, timeout=15)
    
    # print("Length of quotes page HTML:", len(quotes_resp.text))
    # print("Sample HTML snippet:", quotes_resp.text[:1000])

    quotes_resp = handle_redirect(quotes_resp, headers=headers) # handle redirect manually
    quotes_html = HTMLParser(quotes_resp.text)

    next_quotes_result = quotes_html.css_first("a.next_page") # checks for pagination
    quotes_data = []

    page_count = 0 # debugging # tracks number of pages fetched
    while next_quotes_result:
        page_count += 1 # debugging
        print(f"Fetching quotes page {page_count}: {quotes_url}") # debugging

        quotes = quotes_html.css("div.quoteText") # selects all quote blocks

        for quote in quotes:
            quoteBlock = quote.text().strip().split("\n") # cleans up quote text
            quoteText = quoteBlock[0].strip('“”" ') # removes punctuation/extra characters
            author = quote.css_first("span.authorOrTitle").text().strip("\n, ") # gets author
            quotes_data.append({"quote": quoteText, "author": author})

            # print(f"Found quote: {quoteText} – {author}") # debugging

        next_quotes_result = quotes_html.css_first("a.next_page") # checks again for pagination
        if not next_quotes_result:
            break # no next page, exit loop
        
        next_quotes_href = next_quotes_result.attributes.get("href", "") # gets next page link
        if not next_quotes_href:
            break

        if page_count >= max_pages: # stops if max page count is reached
            print(f"Reached max page limit ({max_pages}), stopping.")
            break

        # constructs the next page URL and fetches it
        next_quotes_url = "https://www.goodreads.com" + next_quotes_href
        # print("Fetching next page URL: ", next_quotes_url) # debugging statement for pagination
        next_quotes_resp = httpx.get(next_quotes_url, headers=headers, timeout=15)

        # parses and handles redirects again
        quotes_html = HTMLParser(next_quotes_resp.text)
        next_quotes_resp = handle_redirect(next_quotes_resp, headers=headers) # handle redirect manually
        quotes_html = HTMLParser(next_quotes_resp.text)

    if not quotes_data: # if no quotes were found
        return None

    return quotes_data # returns the collected quotes

def get_quotes_for_book(book_name):
    # Entry point: uses all helpers to get quotes for a given book name
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
    
    # step 1: get book URL from search

    book_url = get_book_url(book_name, headers=headers)
    if not book_url:
        return {"error": "Book not found."}

    # step 2: get quotes page URL from book page
    quotes_url = get_quotes_page_url(book_url, headers=headers)
    if not quotes_url:
        return {"error": "Could not find a quotes page."}

    # step 3: extract quotes from the quotes page
    quotes_data = extract_quotes(quotes_url, headers=headers)
    if not quotes_data:
        return {"error": "No quotes found."}

    return {"quotes": quotes_data} # returns dictionary with all quotes
    # return jsonify(quotes_data)