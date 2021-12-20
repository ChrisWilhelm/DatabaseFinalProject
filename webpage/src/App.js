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
import {IoNewspaperOutline, FaThumbsUp, FaThumbsDown} from "react-icons/all";
import {Button, Popover, PopoverBody, PopoverHeader} from "reactstrap";



const months = [ "January", "February", "March", "April", "May", "June",
"July", "August", "September", "October", "November", "December" ];

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

const ratingColors = {
    "LEFT": "#0275d8",
    "LEAN_LEFT": "#89CFF0",
    "CENTER": "#888888",
    "LEAN_RIGHT": "#ffcccb",
    "RIGHT": "#d9534f",
    "MIXED": "#b19cd9"
}

const ratingStrings = {
    "LEFT": "LEFT",
    "LEAN_LEFT": "LEFT LEANING",
    "CENTER": "CENTER LEANING",
    "LEAN_RIGHT": "RIGHT LEANING",
    "RIGHT": "RIGHT",
    "MIXED": "MIXED"
}


function App() {
    const [articles, setArticles] = useState([]);
    const [searchSent, setSearchSent] = useState(false);
    const [query, setQuery] = useState("");
    const [isLoading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [lastQuery, setLastQuery] = useState("");

    if (!searchSent) {
       return (
            <div className="app-container">
              <header className="App-header">
                  <h1>
                      NewsLine
                  </h1>
                  <SearchBar
                      searchHook={() => {
                          setSearchSent(true);
                          setLastQuery(query);
                      }}
                      setQuery={setQuery}
                      query={query}
                      onSubmit={() => {
                        onSubmit(query, setLoading, setArticles, setError)
                      }}/>
              </header>
            </div>
       );
    } else {
        return (
            <div className="app-container">
              <header className="search-results-header">
                  <SearchBar
                      searchHook={() => {
                          setSearchSent(true);
                          setLastQuery(query);
                      }}
                      setQuery={setQuery}
                      query={query}
                      onSubmit={() => {
                        onSubmit(query, setLoading, setArticles, setError)
                      }}
                  />
              </header>
                {isLoading &&
                <div className="loader-container">
                    <div className="loader" />
                </div>}
                {!isLoading && <div className="timeline-container">
                     <VerticalTimeline>
                        {articles.map((article, index) =>
                            <ArticleBody article={article} key={index} index={index}
                                query={lastQuery}
                            />)}
                    </VerticalTimeline>
                    </div>}
            </div>
        );
    }
}

const RatingIcon = ({rating, index}) => {
    const [isOpen, setIsOpen] = useState(false);
    const onHover = () => {
        setIsOpen(true);
    }

    const popoverName = "Popover" + index.toString();
    const popoverSide = index % 2 === 0 ? "right" : "left";

    const onHoverLeave = () => {
        setIsOpen(false);
    }

    return (
        <Button
            id={popoverName}
            className="rating-button"
            onMouseEnter={onHover}
            onMouseLeave={onHoverLeave}
            style={{
                display: "flex",
                width: '100%',
                height: '100%',
                border: 0,
                backgroundColor: 'transparent'
            }}
        ><IoNewspaperOutline color={"#fff"}/>
            { <Popover target={popoverName}
                      placement={popoverSide}
                      isOpen={isOpen}
                      fade={true}
            >
                <div style={{
                    backgroundColor: "#fff",
                    borderRadius: 12,
                    padding: 5,
                    paddingLeft: 10,
                    paddingRight: 10,
                    margin: 25,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    flexDirection: "column",
                    maxWidth: 250
                }}>
                    <PopoverHeader>Political Bias</PopoverHeader>
                    <PopoverBody
                        style={{
                            marginLeft: 20,
                            marginRight: 20,
                            fontFamily: "Noto Sans SC"
                        }}
                    >This site has a tendency to publish content rated as <p
                        style={{
                        color: ratingColors[rating],
                        textAlign: 'center'
                        }}
                    >{ratingStrings[rating]}
                    </p></PopoverBody>
                </div>
            </Popover>}
        </Button>
    );
}

const ArticleBody = ({article, index, query}) => {
    const date = article.date ? new Date(article.date) : null;
    const dateString = date ? months[date.getMonth()] + " "
        + (date.getDate()) + ", " + date.getFullYear() : "Date not available";
   return (
       <VerticalTimelineElement
        className="vertical-timeline-element--work"
        contentStyle={{ background: 'rgb(33, 150, 243)', color: '#fff',
        }}
        contentArrowStyle={{ borderRight: '7px solid  rgb(33, 150, 243)' }}
        date={dateString}
        icon={<RatingIcon index={index} rating={article.rating} />}
        iconStyle={{ background: 'rgb(33, 150, 243)',
            color: '#fff' }}
       >
           <h2
           style={{
               color: '#fff'
           }}
           >{article.title}</h2>
           <h3
           style={{
               color: '#ccc'
           }}
           >{article.publisher}</h3>
           <h4 className="article-summary">{article.summary}</h4>
           <div style={{
               display: 'flex',
               flexDirection: 'row',
               justifyContent: 'space-between',
           }}>
               <div>
                   <a className={"article-link"}
                       target={"blank"} href={article.link}>Article</a>
                   <a className={"site-link"}
                      target={"blank"}
                      href={article.site}>Site Home Page</a>
               </div>
               <LikeDislikeButton query={query} doc_id={article.doc_id}/>
           </div>
       </VerticalTimelineElement>
   );
}

const actions = {
    SET_RELEVANT: 'SET_RELEVANT',
    SET_IRRELEVANT: 'SET_IRRELEVANT',
    UNDO_RELEVANT: 'UNDO_RELEVANT',
    UNDO_IRRELEVANT: 'UNDO_IRRELEVANT'
}


const updateQueryFromNeutral = (doc_id, query, action) => {
    const relevant = [];
    const irrelevant = [];
    if (action === actions.SET_RELEVANT) {
        relevant.push(doc_id);
    } else if (action === actions.SET_IRRELEVANT) {
        irrelevant.push(doc_id);
    }
    const body = {
        q: query,
        undo: "False",
        relevant: relevant,
        irrelevant: irrelevant
    }
    fetch(HOST + "/query/update", {
        method: 'POST',
        headers: {
            "Accept": "*/*",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    }).then(resp => resp).catch(error => error)
}

const updateQueryFromOpposite = (doc_id, query, action) => {
    const relevant = [];
    const irrelevant = [];
    if (action === actions.SET_RELEVANT) {
        relevant.push(doc_id);
        relevant.push(doc_id);
    } else if (action === actions.SET_IRRELEVANT) {
        irrelevant.push(doc_id);
        irrelevant.push(doc_id);
    }
    const body = {
        q: query,
        undo: "False",
        relevant: relevant,
        irrelevant: irrelevant
    }
    fetch(HOST + "/query/update", {
        method: 'POST',
        headers: {
            "Accept": "*/*",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    }).then(resp => resp).catch(error => error)
}

const updateQueryToNeutral = (doc_id, query, action) => {
    const relevant = [];
    const irrelevant = [];
    if (action === actions.UNDO_RELEVANT) {
        relevant.push(doc_id);
    } else if (action === actions.UNDO_IRRELEVANT) {
        irrelevant.push(doc_id);
    }
    const body = {
        q: query,
        undo: "True",
        relevant: relevant,
        irrelevant: irrelevant,
    }
    fetch(HOST + "/query/update", {
        method: 'POST',
        headers: {
            "Accept": "*/*",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    }).then(resp => console.log(resp)).catch(error => error)
}


const LikeDislikeButton = ({doc_id, query}) => {
    const [likedState, setLikedState] = useState(0);

    const changeStateWithLikeButton = () => {
        if (likedState === 1) {
            setLikedState(0);
        } else {
            setLikedState(1);
        }
    }

    const changeStateWithDislikeButton = () => {
        if (likedState === -1) {
            setLikedState(0);
        } else {
            setLikedState(-1);
        }
    }

    const updateOrUndoQueryWithLike = (query, doc_id) => {
        if (!doc_id || !query) return;

        if (likedState === -1) {
            updateQueryFromOpposite(doc_id, query, actions.SET_RELEVANT);
        } else if (likedState === 0) {
            updateQueryFromNeutral(doc_id, query, actions.SET_RELEVANT);
        } else {
            updateQueryToNeutral(doc_id, query, actions.UNDO_RELEVANT);
        }
    }

    const updateOrUndoQueryWithDislike = (query, doc_id) => {
        if (!doc_id || !query) return;

        if (likedState === 1) {
            updateQueryFromOpposite(doc_id, query, actions.SET_IRRELEVANT);
        } else if (likedState === 0) {
            updateQueryFromNeutral(doc_id, query, actions.SET_IRRELEVANT);
        } else {
            updateQueryToNeutral(doc_id, query, actions.UNDO_IRRELEVANT);
        }
    }

    return (
        <div>
            <button
                style={{
                    backgroundColor: likedState === 1 ? '#90ee90' : null
                }}
                onClick={() => {
                    changeStateWithLikeButton();
                    updateOrUndoQueryWithLike(query, doc_id);
                }}
                className={'thumb-button thumbs-up'}><FaThumbsUp /></button>
            <button
                style={{
                    backgroundColor: likedState === -1 ? '#ff6961' : null
                }}
                onClick={() => {
                    changeStateWithDislikeButton();
                    updateOrUndoQueryWithDislike(query, doc_id);
                }}
                className={'thumb-button thumbs-down'}><FaThumbsDown /></button>
        </div>
    );
}

const object2xwww = (obj) => Object.keys(obj).map(key =>
encodeURIComponent(key) + '=' + encodeURIComponent(obj[key])).join('&');

export default App;
