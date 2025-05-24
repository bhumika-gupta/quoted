import httpx
from selectolax.parser import HTMLParser
import sys # access command line arguments
import json
"""
    "Page 1": "https://quotes.toscrape.com/page/1/",
    "Page 2": "https://quotes.toscrape.com/page/2/",
    "Page 3": "https://quotes.toscrape.com/page/3/"
    """
BOOK_URLS = {
    
    "Page 1": "https://www.goodreads.com/quotes?page=1&ref=nav_comm_quotes",
    "Page 2": "https://www.goodreads.com/quotes?page=2&ref=nav_comm_quotes",
    "Page 3": "https://www.goodreads.com/quotes?page=3&ref=nav_comm_quotes"
}
# print("Select a page to scrape:")
print("Search for a book!") 

user_book = input("Enter a book name: ")
search_result = "https://www.goodreads.com/search?q=" + user_book.replace(" ", "+") # TODO: better format into search result

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}

# get search results
search_resp = httpx.get(search_result, headers=headers)
search_html = HTMLParser(search_resp.text)

# get first book result (soon, maybe the user can click which one, in case it's not showing the correct one)
first_result = search_html.css_first("a.bookTitle")
first_result_href = first_result.attributes["href"]
book_url = "https://www.goodreads.com" + first_result_href

# visit book page to find the quotes link
book_resp = httpx.get(book_url, headers=headers)
book_html = HTMLParser(book_resp.text)

quotes_link = book_html.css_first("a.DiscussionCard")
quotes_url = quotes_link.attributes["href"]

print("Book page:", book_url)
print("Quotes page:", quotes_url)

quotes_resp = httpx.get(quotes_url, headers=headers)
quotes_html = HTMLParser(quotes_resp.text)

# debugging
# print("Length of quotes page HTML:", len(quotes_resp.text))
# print("Sample HTML snippet:", quotes_resp.text[:1000])

# handle redirect manually
redirect_link = quotes_html.css_first("a")
if redirect_link:
    redirected_url = redirect_link.attributes["href"]
    print("Redirecting to actual quotes page:", redirected_url)
    quotes_resp = httpx.get(redirected_url, headers=headers)
    quotes_html = HTMLParser(quotes_resp.text)

quotes_data = []

quotes = quotes_html.css("div.quoteText")

for quote in quotes:
        quoteBlock = quote.text().strip().split("\n")
        quoteText = quoteBlock[0].strip('“”" ')
        # quote = quoteText[1]
        author = quote.css_first("span.authorOrTitle").text().strip("\n, ")
        quotes_data.append({"quote": quoteText, "author": author})

        # print(f"Found quote: {quoteText} – {author}")

# save to JSON
with open("quotes.json", "w", encoding="utf-8") as f:
    json.dump(quotes_data, f, indent=2, ensure_ascii=False)

html_output = "<html><body><h1>Quotes</h1><ul>"
for data in quotes_data: 
    html_output += f"<li>{data['quote']} – <em>{data['author']}</em></li>"
html_output += "</ul></body></html>"

with open("quotes.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("Quotes saved to 'quotes.json' and 'quotes.html'")







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
