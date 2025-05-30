import httpx
from selectolax.parser import HTMLParser
# import sys # access command line arguments
# import json

# given a book name, get its Goodreads page URL
def get_book_url(book_name, headers):
    # get search results
    search_result = "https://www.goodreads.com/search?q=" + book_name.replace(" ", "+") # TODO: better format into search result
    search_resp = httpx.get(search_result, headers=headers)
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
    book_resp = httpx.get(book_url, headers=headers)
    book_html = HTMLParser(book_resp.text)

    quotes_link = book_html.css_first("a.DiscussionCard")
    quotes_url = quotes_link.attributes["href"]

    # print("Book page:", book_url) # keep for now (debugging)
    # print("Quotes page:", quotes_url) # keep for now (debugging)

    if not quotes_link or not quotes_url: # not sure which one
        return None # print("No quotes link found.")

    return quotes_url

# if redirected to an intermediate page, follow to the final quotes page
def handle_redirect(resp, headers):
    html = HTMLParser(resp.text)
    redirect_link = html.css_first("a")
    if redirect_link:
        redirected_url = redirect_link.attributes.get("href", "")
        if "quotes" in redirected_url and "goodreads.com" in redirected_url and "blog" not in redirected_url:
                new_resp = httpx.get(redirected_url, headers=headers) # print("Redirecting to actual quotes page:", redirected_url)
                return new_resp
                
    return resp

# extract all quotes from the quotes page (supports pagination)
def extract_quotes(quotes_url, headers):
    quotes_resp = httpx.get(quotes_url, headers=headers)
    # quotes_resp = handle_redirect(quotes_resp, headers=headers) # handle redirect manually
    quotes_html = HTMLParser(quotes_resp.text)

    # debugging
    # print("Length of quotes page HTML:", len(quotes_resp.text))
    # print("Sample HTML snippet:", quotes_resp.text[:1000])

    quotes_resp = handle_redirect(quotes_resp, headers=headers) # handle redirect manually
    quotes_html = HTMLParser(quotes_resp.text)

    # support pagination
    next_quotes_result = quotes_html.css_first("a.next_page")
    quotes_data = []

    while next_quotes_result:
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

        next_quotes_url = "https://www.goodreads.com" + next_quotes_href
        # print("Fetching next page URL: ", next_quotes_url) # debugging statement for pagination
        next_quotes_resp = httpx.get(next_quotes_url, headers=headers)

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

"""def save_results(quotes_data):
     # save to JSON
    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(quotes_data, f, indent=2, ensure_ascii=False)

    html_output = "<html><body><h1>Quotes</h1><ul>"
    for data in quotes_data: 
        html_output += f"<li>{data['quote']} – <em>{data['author']}</em></li>"
    html_output += "</ul></body></html>"

    with open("quotes.html", "w", encoding="utf-8") as f:
        f.write(html_output)"""


"""def main():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}

    print("Search for a book!")
    while True:
        user_book = input("Enter a book name: ")
        book_url = get_book_url(user_book, headers=headers)
        if not book_url:
            print("Book not found.")
            tryagain = input("Would you like to try again to search for a book? Please enter 'Yes' or 'No': ")
            if tryagain == "Yes" or tryagain == "yes":
                continue
            else: 
                break

        quotes_url = get_quotes_page_url(book_url, headers=headers)
        if not quotes_url:
            print("Could not find a quotes page.")
            tryagain = input("Would you like to try again to search for a book? Please enter 'Yes' or 'No': ")
            if tryagain == "Yes" or tryagain == "yes":
                continue
            else: 
                break

        quotes_data = extract_quotes(quotes_url, headers)
        if not quotes_data:
            print("No quotes found for this book.")
            tryagain = input("Would you like to try again to search for a book? Please enter 'Yes' or 'No': ")
            if tryagain == "Yes" or tryagain == "yes":
                continue
            else: 
                break

        # would want to ask user if they want to search for another book, once the saving feature is better
        save_results(quotes_data)
        print("Quotes saved to 'quotes.json' and 'quotes.html'")
        break

main()"""




"""for i, title in enumerate(BOOK_URLS, 1):
    print(f"{i}. {title}")
choice = int(input("Enter a number: "))
url = list(BOOK_URLS.values()   )[choice - 1]"""

"""# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)

quotes_data = []

books = html.css("div.quoteText")

for book in books:
        quoteText = book.css_first("div.quoteText").text().split("\n")
        quote = quoteText[1]
        author = book.css_first("span.authorOrTitle").text()
        quotes_data.append({"quote": quote, "author": author})

# save to JSON
with open("quotes.json", "w", encoding="utf-8") as f:
    json.dump(quotes_data, f, indent=2, ensure_ascii=False)

html_output = "<html><body><h1>Quotes</h1><ul>"
for data in quotes_data: 
    html_output += f"<li>{data['quote']} – <em>{data['author']}</em></li>"
html_output += "</ul></body></html>"

with open("quotes.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("Quotes saved to 'quotes.json' and 'quotes.html'")"""


"""if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://quotes.toscrape.com"
    results = scrape_quotes(url)

    

    for quote, author in results:
        print(f"{quote} – {author}")"""

