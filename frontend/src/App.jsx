import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import './App.css'

function App() {
  // state variables
  const [book, setBook] = useState(""); // book stores current input from user, setBook updates the value
  const [quotes, setQuotes] = useState([]); // stores list list of quote results from Flask API, starts as an empty array
  const [loading, setLoading] = useState(false); // loading is a flag to show whether we're currently waiting for a response from the server
  const [error, setError] = useState(null); // error message if the fetch fails or returns an error
  const [searchResults, setSearchResults] = useState([]);
  // const [bookHref, setBookHref] = useState("")
  const [currentPage, setCurrentPage] = useState(1);

  // fetch search results from Flask backend based on user input
  const searchQuotes = async() => {
    if (!book.trim()) return; // do nothing if input is empty
    const response = await fetch(`/api/search_results?userBook=${encodeURIComponent(book)}`);
    // const text = await response.text(); # debugging
    // console.log("Raw response text:", text); # debugging

    try {
      const data = await response.json(); // parse JSON
      setError(null); // clear previous errors
      setQuotes([]); // clear previous quotes
      setSearchResults(data.results); // update search results
    } catch (e) {
      console.error("JSON parse error:", e);
      setError("Invalid response from server.");
    }
  }

  // fetch quotes for selected book using href from search results
  const fetchQuotes = async (bookHref) => {
    setLoading(true); // start loading message
    setError(null); // clear previous errors

    try {
      const response = await fetch(`http://localhost:5050/api/quotes?href=${encodeURIComponent(bookHref)}`); // sends a GET request to Flask backend & adds input bookname into the URL
      const data = await response.json(); // parse JSON response
      console.log("Response data from backend: ", data); // debugging

      if (data.error) {
        setError(data.error); // show any error returned from Flask
        setSearchResults([]); // clear search results if there's an error
        setQuotes([]); // clear quotes if there's an error
      } else if (Array.isArray(data.quotes)) {
        setQuotes(data.quotes);
        setError(null);
      } else {
        setQuotes([]);
        setError("Unexpected response format.");
      }
    } catch (err) {
        setError("Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  // optional: test the backend is reachable
  const testBackend = async () => {
    try {
      const res = await fetch("http://localhost:5050/test")
      const data = await res.json();
      console.log("Backend test response:", data);
      alert(data.message);
    } catch (err) {
      console.error("Failed to connect to backend: ", err);
      alert("Error reaching backend");
    }
  };
  var quotes_per_page = 15;
  var start_index = (currentPage - 1) * quotes_per_page;
  var end_index = currentPage * quotes_per_page;

  var numPages = Math.ceil(quotes.length / quotes_per_page);

  const handleNext = () => {
    setCurrentPage(currentPage+1)
  };

  const handlePrev = () => {
    setCurrentPage(currentPage-1)
  };

  var pageNumberWindow = 2; // show 2 pages before and after the currentPage
  var startPageWindow = Math.max(1, currentPage - pageNumberWindow);
  var endPageWindow = Math.min(numPages, currentPage + pageNumberWindow);

  // render UI
  return (
      <div className="App" style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>quoted</h1>

        {/* book input field */}
        <input
          type="text"
          value={book}
          onChange={(e) => setBook(e.target.value)}
          placeholder="Enter book title"
          style={{ padding: "0.5rem", width: "300px" }}
        />

        {/* search button */}
        <button onClick={searchQuotes} style={{ marginLeft: "1rem", padding: "0.5rem" }}>
          Search
        </button>

        {/* optional: button to test connection to backend */}
        <button onClick={testBackend} style={{ marginTop: "1rem", marginLeft: "1rem", padding: "0.5rem" }}>
          Test Backend
        </button>

        {/* loading and error messages */}
        {loading ? <p>Loading...</p> : null}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {/* show book search results if quotes haven't been fetched yet */}
        {!loading && quotes.length === 0 && (
        <ul>
          {searchResults.map((result, idx) => (
            <div key={idx}>
                <p>{result.bookTitle} by {result.bookAuthor}, published {result.publishedYear}</p>
                <button onClick={() => fetchQuotes(result.href)}>Get Quotes</button>
            </div>
          ))}
        </ul>)
        }
        
        {/* initial message if no quotes and no search yet */}
        {!loading && searchResults.length === 0 && !error && quotes.length === 0 && (
          <p>No quotes to display. Try searching for a book!</p>
        )}

        {/* show 15 quotes at a time */}
        <ul>
          {Array.isArray(quotes) && quotes.slice(start_index, end_index).map((q, idx) => (
            <li key={start_index + idx}> {/* idx alone is not unique "key" prop due to dynamic nature of slicing array and pagination */}
                {q.quote} - <em>{q.author}</em>
            </li>
          ))}
        </ul>

        {/* previous button if currentPage > 1 */}
        {Array.isArray(quotes) && currentPage > 1 && (
        <button onClick={handlePrev} style={{ marginLeft: "1rem", padding: "0.5rem" }}>
          Previous
        </button>)
        }

        {/* render page numbers */}
        {Array.isArray(quotes) && numPages > 1 && 
          Array.from({length: endPageWindow - startPageWindow + 1}, (_, i) => startPageWindow + i).map((n, idx) => 
          <button 
            key={n}
            onClick={() => setCurrentPage(n)} 
            style={{ marginLeft: "1rem", padding: "0.4rem" }}
            className={n === currentPage ? "active-page" : ""}>
            {n}
          </button>
        )}

        {/* next button if currentPage < numPages */}
        {Array.isArray(quotes) && currentPage < numPages && (
        <button onClick={handleNext} style={{ marginLeft: "1rem", padding: "0.5rem" }}>
          Next
        </button>)
        }
        </div>
  );
}

export default App;


// in return statement:
/* <div>
        <! <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>  */