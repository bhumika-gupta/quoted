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
print("Select a page to scrape:")
for i, title in enumerate(BOOK_URLS, 1):
    print(f"{i}. {title}")
choice = int(input("Enter a number: "))
url = list(BOOK_URLS.values()   )[choice - 1]

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)

quotes_data = []
# books = html.css("div.quote")
books = html.css("div.quoteText")

for book in books:
        # quote = book.css_first("span.text").text()
        # author = book.css_first("small.author").text()
        # print(f"{quote} – {author}")
        # quote = book.css_first("div.quoteText").text()
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

print("Quotes saved to 'quotes.json' and 'quotes.html'")


"""if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://quotes.toscrape.com"
    results = scrape_quotes(url)

    

    for quote, author in results:
        print(f"{quote} – {author}")"""
