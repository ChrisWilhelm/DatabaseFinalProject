import logo from './logo.svg';
import './App.css';
import SearchBar from "./components/searchBar";
import {useState} from 'react';
import {
    VerticalTimeline,
    VerticalTimelineElement
}  from 'react-vertical-timeline-component';

function App() {
    const [articles, setArticles] = useState([]);
    const [searchSent, setSearchSent] = useState(false);
    const [query, setQuery] = useState("");

    if (!searchSent) {
       return (
            <div>
              <header className="App-header">
                  <h1>
                      NewsLine
                  </h1>
                  <SearchBar searchHook={setSearchSent} setQuery={setQuery} query={query} />
                  {console.log(searchSent)}
              </header>
            </div>
       );
    } else {
        return (
            <div>
              <header className="search-results-header">
                  <SearchBar searchHook={setSearchSent} setQuery={setQuery} query={query} />
                  {console.log(searchSent)}
              </header>
                <VerticalTimeline >

                </VerticalTimeline>
            </div>
        );
    }
}

export default App;
