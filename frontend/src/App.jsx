import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

function App() {
  // const [count, setCount] = useState(0)
  const [book, setBook] = useState(""); // book stores current input from user, setBook updates the value
  const [quotes, setQuotes] = useState([]); // stores list list of quote results from Flask API, starts as an empty array
  const [loading, setLoading] = useState(false); // loading is a flag to show whether we're currently waiting for a response from the server
  const [error, setError] = useState(null); // error message if the fetch fails or returns an error

  // function to call backend API and update UI with quotes
  const searchQuotes = async () => { 
    if (!book.trim()) return; // do nothing if input is empty
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/search?book=${encodeURIComponent(book)}`); // sends a GET request to Flask backend & adds input bookname into the URL
      const data = await response.json(); // parse JSON response

      if (data.error) {
        setError(data.error); // show any error returned from Flask
        setQuotes([]); // clear quotes if there's an error
      } else {
        setQuotes(data.quotes); // update quotes state
      }
    } catch (err) {
        setError("Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  return (
      <div className="App" style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>quoted</h1>
        <input
          type="text"
          value={book}
          onChange={(e) => setBook(e.target.value)}
          placeholder="Enter book title"
          style={{ padding: "0.5rem", width: "300px" }}
        />
        <button onClick={searchQuotes} style={{ marginLeft: "1rem", padding: "0.5rem" }}>
          Search
        </button>
        
        {loading ? <p>Loading...</p> : null}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        <ul>
          {quotes.map((q, idx) => (
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
{/* <div>
        <! <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>  */}