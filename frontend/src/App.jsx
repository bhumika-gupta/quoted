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

  // fetch search results from Flask backend based on user input
  const searchQuotes = async() => {
    if (!book.trim()) return; // do nothing if input is empty
    const response = await fetch(`/api/search_results?userBook=${encodeURIComponent(book)}`);
    // const text = await response.text(); # debugging
    // console.log("Raw response text:", text); # debugging

    try {
      const data = await response.json(); // parse JSON
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
        { !loading && quotes.length === 0 && (
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
        
        {/* show retrieved quotes */}
        <ul>
          {Array.isArray(quotes) && quotes.map((q, idx) => (
            <li key={idx}>
                {q.quote} - <em>{q.author}</em>
            </li>
          ))}
        </ul>
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