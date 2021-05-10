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
import {IoNewspaperOutline} from "react-icons/all";
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
                    {articles.map((article, index) =>
                        <ArticleBody article={article} key={index} index={index} />)}
                </VerticalTimeline>
                    </div>
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
                    <PopoverHeader>Potential Bias</PopoverHeader>
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

const ArticleBody = ({article, index}) => {
    const date = article.date ? new Date(article.date) : null;
    const dateString = date ? months[date.getMonth()] + " "
        + (date.getDate()) + ", " + date.getFullYear() : "unlisted";
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
           <div>
               <a className={"article-link"}
                   target={"blank"} href={article.link}>Link</a>
               <a className={"site-link"} target={"blank"} href={article.site}>Site Home Page</a>
           </div>
       </VerticalTimelineElement>
   );
}



export default App;
