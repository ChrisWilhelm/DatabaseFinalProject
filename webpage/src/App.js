import logo from './logo.svg';
import './App.css';
import SearchBar from "./components/searchBar";
import {useState} from 'react';
import {
    VerticalTimeline,
    VerticalTimelineElement
}  from 'react-vertical-timeline-component';
import {HOST} from "./config";
import 'react-vertical-timeline-component/style.min.css';

function onSubmit(query, setLoading, setArticles, setError) {
    setLoading(true);
    setError(false);
    const url = HOST + "/query?q=" + query
    console.log(url);
    fetch(url, {
        headers: {
            "Accept": "*/*",
            "Content-Type": "application/json"
        },
    }).then((resp) => {
        setLoading(false);
        const statusCode = resp.status;
        if (statusCode === 200) {
            return resp.json();
        } else {
            setError(true);
        }
    }).then((json) => {
        setArticles(json["results"])
    }).catch(error => error);
}


function App() {
    const [articles, setArticles] = useState([]);
    const [searchSent, setSearchSent] = useState(false);
    const [query, setQuery] = useState("");
    const [isLoading, setLoading] = useState(false);
    const [error, setError] = useState(false);

    if (!searchSent) {
       return (
            <div className="app-container">
              <header className="App-header">
                  <h1>
                      NewsLine
                  </h1>
                  <SearchBar
                      searchHook={setSearchSent}
                      setQuery={setQuery}
                      query={query}
                      onSubmit={() => {
                        onSubmit(query, setLoading, setArticles, setError)
                      }}/>
                  {console.log(searchSent)}
              </header>
            </div>
       );
    } else {
        return (
            <div className="app-container">
              <header className="search-results-header">
                  <SearchBar
                      searchHook={setSearchSent}
                      setQuery={setQuery}
                      query={query}
                      onSubmit={() => {
                        onSubmit(query, setLoading, setArticles, setError)
                      }}
                  />
              </header>
                <div className="timeline-container">
                <VerticalTimeline>
                    {articles.map(article => {
                       return (
                           <VerticalTimelineElement
                            className="vertical-timeline-element--work"
                            contentStyle={{ background: 'rgb(33, 150, 243)', color: '#fff' }}
                            contentArrowStyle={{ borderRight: '7px solid  rgb(33, 150, 243)' }}
                            date="2011 - present"
                            iconStyle={{ background: 'rgb(33, 150, 243)', color: '#fff' }}
                           >
                               <h3>{article.title}</h3>
                               <h4 className="article-summary">{article.summary}</h4>
                               <a className={"article-link"}
                                   target={"blank"} href={article.link}>Link</a>
                           </VerticalTimelineElement>
                       );
                    })}
                </VerticalTimeline>
                    </div>
            </div>
        );
    }
}

export default App;
