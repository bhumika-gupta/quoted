import httpx
from selectolax.parser import HTMLParser
# import sys # access command line arguments
import json

# given a book name, get its Goodreads page URL
def get_book_url(book_name, headers):
    # get search results
    search_result = "https://www.goodreads.com/search?q=" + book_name.replace(" ", "+") # TODO: better format into search result
    search_resp = httpx.get(search_result, headers=headers, timeout=10)
    search_html = HTMLParser(search_resp.text)

    # get first book result (soon, maybe the user can click which one, in case it's not showing the correct one) 

    first_result = search_html.css_first("a.bookTitle")
    if not first_result:
        return None # print("No book results found.")

    first_result_href = first_result.attributes["href"]
    book_url = "https://www.goodreads.com" + first_result_href
    
    return book_url

# from a Goodreads book URL, get the quotes subpage URL
def get_quotes_page_url(book_url, headers):
    # visit book page to find the quotes link
    book_resp = httpx.get(book_url, headers=headers, timeout=10)
    book_html = HTMLParser(book_resp.text)

    quotes_link = book_html.css_first("a.DiscussionCard")
    if not quotes_link:
        return None
    
    quotes_url = quotes_link.attributes["href"]

    # print("Book page:", book_url) # keep for now (debugging)
    # print("Quotes page:", quotes_url) # keep for now (debugging)

    if not quotes_url:
        return None # print("No quotes link found.")

    return quotes_url

# if redirected to an intermediate page, follow to the final quotes page
def handle_redirect(resp, headers):
    html = HTMLParser(resp.text)
    redirect_link = html.css_first("a")
    if redirect_link:
        redirected_url = redirect_link.attributes.get("href", "")
        if "quotes" in redirected_url and "goodreads.com" in redirected_url and "blog" not in redirected_url:
                new_resp = httpx.get(redirected_url, headers=headers, timeout=10) # print("Redirecting to actual quotes page:", redirected_url)
                return new_resp
                
    return resp

# extract all quotes from the quotes page (supports pagination)
def extract_quotes(quotes_url, headers, max_pages=10):
    quotes_resp = httpx.get(quotes_url, headers=headers, timeout=10)
    # quotes_resp = handle_redirect(quotes_resp, headers=headers) # handle redirect manually
    
    # quotes_html = HTMLParser(quotes_resp.text) # should keep this line in?

    # debugging
    # print("Length of quotes page HTML:", len(quotes_resp.text))
    # print("Sample HTML snippet:", quotes_resp.text[:1000])

    quotes_resp = handle_redirect(quotes_resp, headers=headers) # handle redirect manually
    quotes_html = HTMLParser(quotes_resp.text)

    # support pagination
    next_quotes_result = quotes_html.css_first("a.next_page")
    quotes_data = []

    page_count = 0 # debugging
    while next_quotes_result:
        page_count += 1 # debugging
        print(f"Fetching quotes page {page_count}: {quotes_url}") # debugging

        quotes = quotes_html.css("div.quoteText")

        for quote in quotes:
                quoteBlock = quote.text().strip().split("\n")
                quoteText = quoteBlock[0].strip('“”" ')
                author = quote.css_first("span.authorOrTitle").text().strip("\n, ")
                quotes_data.append({"quote": quoteText, "author": author})

                # print(f"Found quote: {quoteText} – {author}") # debugging
    
        next_quotes_result = quotes_html.css_first("a.next_page")
        if not next_quotes_result:
            break # no next page, exit loop
        
        next_quotes_href = next_quotes_result.attributes.get("href", "")
        if not next_quotes_href:
            break

        if page_count >= max_pages:
            print(f"Reached max page limit ({max_pages}), stopping.")
            break

        next_quotes_url = "https://www.goodreads.com" + next_quotes_href
        # print("Fetching next page URL: ", next_quotes_url) # debugging statement for pagination
        next_quotes_resp = httpx.get(next_quotes_url, headers=headers, timeout=10)

        quotes_html = HTMLParser(next_quotes_resp.text)
        
        next_quotes_resp = handle_redirect(next_quotes_resp, headers=headers) # handle redirect manually
        quotes_html = HTMLParser(next_quotes_resp.text)


    if not quotes_data:
        return None

    return quotes_data

# main entry point for backend: given a book name, return extracted quotes
def get_quotes_for_book(book_name):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
    
    book_url = get_book_url(book_name, headers=headers)
    if not book_url:
        return {"error": "Book not found."}

    quotes_url = get_quotes_page_url(book_url, headers=headers)
    if not quotes_url:
        return {"error": "Could not find a quotes page."}

    quotes_data = extract_quotes(quotes_url, headers=headers)
    if not quotes_data:
        return {"error": "No quotes found."}

    return {"quotes": quotes_data}
    # return jsonify(quotes_data)