import React, {useState} from 'react';

function getWindowDimensions() {
  const { innerWidth: width, innerHeight: height } = window;
  return {
    width,
    height
  };
}

const {width, height} = getWindowDimensions();


const search = (query) => {
    return [];
}

function SearchBar({query, setQuery, searchHook}) {

    return (
            <form
                className='search-bar'
                style={{
                display: 'flex',
                height: 75,
                width: width * 0.6,
                borderRadius: 50,
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <label
                    className="search-bar-label"
                    style={{
                    marginLeft: 50,
                    marginRight: 10,
                }}>
                    <p>
                    Search:
                    </p>
                </label>
                <input
                    className="search-input"
                    type="text"
                       value={query}
                       onChange={event => setQuery(event.target.value)}
                       style={{
                           border: 0,
                           padding: 10,
                           fontSize: 25,
                           flex: 1
                       }}
                />
                <button className="search-button" onClick={(e) => {
                    e.preventDefault();
                    search(query);
                    searchHook(true);
                }}
                    style={{
                        border: 0,
                        paddingLeft: 35,
                        paddingRight: 50,
                        borderBottomRightRadius: 50,
                        borderTopRightRadius: 50,
                        height: '100%',
                        justifyContent: 'center',
                        alignItems: 'center',
                        display: 'flex',
                        backgroundColor: '#89cff0'
                    }}
                >
                    <p style={{
                        fontSize: 24,
                    }}>Submit</p>
                </button>
            </form>
    );
}

export default SearchBar;