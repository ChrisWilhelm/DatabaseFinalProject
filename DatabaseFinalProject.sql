SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Author;
CREATE TABLE Author (
    AuthorID INTEGER PRIMARY KEY NOT NULL auto_increment,
    AName TEXT NOT NULL
);
DROP TABLE IF EXISTS WroteBy;
CREATE TABLE WroteBy (
    ArticleID INTEGER NOT NULL,
    AuthorID INTEGER NOT NULL,
    PRIMARY KEY(ArticleID, AuthorID),
    FOREIGN KEY (ArticleID)
		REFERENCES Articles (ArticleID),
	FOREIGN KEY (AuthorID)
		REFERENCES Author (AuthorID)
);
DROP TABLE IF EXISTS KeyWord;
CREATE TABLE KeyWord (
    KeyWordID INTEGER PRIMARY KEY NOT NULL auto_increment,
    KeyWord TEXT NOT NULL
);
DROP TABLE IF EXISTS HasKeyWord;
CREATE TABLE HasKeyWord (
    KeyWordID INTEGER NOT NULL,
    ArticleID INTEGER NOT NULL,
    PRIMARY KEY (KeyWordID, ArticleID),
    FOREIGN KEY (KeyWordID)
		REFERENCES KeyWord(KeyWordID),
	FOREIGN KEY (ArticleID)
		REFERENCES Articles(ArticleID)
);
DROP TABLE IF EXISTS BiasType;
CREATE TABLE BiasType (
    BiasID INTEGER PRIMARY KEY NOT NULL,
    BiasName VARCHAR(10) NOT NULL
);
INSERT INTO BiasType VALUES (1, 'Left');
INSERT INTO BiasType VALUES (2, 'Lean Left');
INSERT INTO BiasType VALUES (3, 'Center');
INSERT INTO BiasType VALUES (4, 'Lean Right');
INSERT INTO BiasType VALUES (5, 'Right');
INSERT INTO BiasType VALUES (6, 'Mixed');
DROP TABLE IF EXISTS Articles;
CREATE TABLE Articles (
    ArticleID INTEGER NOT NULL PRIMARY KEY auto_increment,
    AName TEXT NOT NULL,
    URL TEXT NOT NULL,
    PublishDate DATETIME,
    NewsSourceID INTEGER,
    ArticleText TEXT,
    ArticleSummary TEXT NOT NULL,
    FOREIGN KEY (NewsSourceID)
		REFERENCES NewsSource(NewsSourceID)
);
DROP TABLE IF EXISTS NewsSource;
CREATE TABLE NewsSource (
    NewsSourceID INTEGER NOT NULL PRIMARY KEY auto_increment,
    NewsSourceName TEXT NOT NULL,
    Homepage TEXT NOT NULL,
    BiasID INTEGER,
    FOREIGN KEY (BiasID)
		REFERENCES BiasType(BiasID)
);
-- INSERT INTO NewsSource VALUES (1, 'AlterNet', 'https://www.alternet.org/', 1);
-- INSERT INTO NewsSource VALUES (2, 'ABC News', 'https://abcnews.go.com/', 2);
-- INSERT INTO NewsSource VALUES (3, 'Associated Press', 'https://apnews.com/', 3);
-- INSERT INTO NewsSource VALUES (4, 'Axios', 'https://www.axios.com/', 3);
-- INSERT INTO NewsSource VALUES (5, 'BBC News', 'https://www.bbc.com/news', 3);
-- INSERT INTO NewsSource VALUES (6, 'Bloomberg', 'https://www.bloomberg.com/', 2);
-- INSERT INTO NewsSource VALUES (7, 'Breitbart News', 'https://www.breitbart.com/', 5);
-- INSERT INTO NewsSource VALUES (8, 'BuzzFeedNews', 'https://www.buzzfeednews.com/', 1);
-- INSERT INTO NewsSource VALUES (9, 'CBS News', 'https://www.cbsnews.com/', 2);
-- INSERT INTO NewsSource VALUES (10, 'Christian Science Monitor', 'https://www.csmonitor.com/', 3);
-- INSERT INTO NewsSource VALUES (11, 'CNN', 'https://www.cnn.com/', 1);
-- INSERT INTO NewsSource VALUES (12, 'CNN Opinion', 'https://www.cnn.com/opinions', 1);
-- INSERT INTO NewsSource VALUES (13, 'Daily Beast', 'https://www.thedailybeast.com/', 1);
-- INSERT INTO NewsSource VALUES (14, 'Daily Mail', 'https://www.dailymail.co.uk/', 5);
-- INSERT INTO NewsSource VALUES (15, 'Democracy Now', 'https://www.democracynow.org/', 1);
-- INSERT INTO NewsSource VALUES (16, 'Forbes', 'https://www.forbes.com/', 3);
-- INSERT INTO NewsSource VALUES (17, 'Fox News', 'https://www.foxnews.com/', 5);
-- INSERT INTO NewsSource VALUES (18, 'Fox News Opinion', 'https://www.foxnews.com/opinion', 5);
-- INSERT INTO NewsSource VALUES (19, 'HuffPost', 'https://www.huffpost.com/', 1);
-- INSERT INTO NewsSource VALUES (20, 'Mother Jones', 'https://www.motherjones.com/', 1);
-- INSERT INTO NewsSource VALUES (21, 'MSNBC', 'https://www.msnbc.com/', 1);
-- INSERT INTO NewsSource VALUES (22, 'National Review', 'https://www.nationalreview.com/', 5); 
-- INSERT INTO NewsSource VALUES (23, 'NBC News', 'https://www.nbcnews.com/', 2); 
-- INSERT INTO NewsSource VALUES (24, 'New York Post', 'https://nypost.com/', 4); 
-- INSERT INTO NewsSource VALUES (25, 'New York Times', 'https://www.nytimes.com/', 2); 
-- INSERT INTO NewsSource VALUES (26, 'New York Times Opinion', 'https://www.nytimes.com/section/opinion', 1); 
-- INSERT INTO NewsSource VALUES (27, 'Newsweek', 'https://www.newsweek.com/', 3); 
-- INSERT INTO NewsSource VALUES (28, 'NPR', 'https://www.npr.org/', 3); 
-- INSERT INTO NewsSource VALUES (29, 'NPR Opinion', 'https://www.npr.org/sections/opinion/', 2); 
-- INSERT INTO NewsSource VALUES (30, 'Politico', 'https://www.politico.com/', 2); 
-- INSERT INTO NewsSource VALUES (31, 'Reason', 'https://reason.com/', 4); 
-- INSERT INTO NewsSource VALUES (32, 'Slate', 'https://slate.com/', 1); 
-- INSERT INTO NewsSource VALUES (33, 'The American Spectator', 'https://spectator.org/', 5); 
-- INSERT INTO NewsSource VALUES (34, 'The Atlantic', 'https://www.theatlantic.com/', 2); 
-- INSERT INTO NewsSource VALUES (35, 'The Daily Caller', 'https://dailycaller.com/', 5); 
-- INSERT INTO NewsSource VALUES (36, 'The Daily Wire', 'https://www.dailywire.com/', 5); 
-- INSERT INTO NewsSource VALUES (37, 'The Economist', 'https://www.economist.com/', 2); 
-- INSERT INTO NewsSource VALUES (38, 'The Epoch Times', 'https://www.theepochtimes.com/', 4); 
-- INSERT INTO NewsSource VALUES (39, 'The Federalist', 'https://thefederalist.com/', 5); 
-- INSERT INTO NewsSource VALUES (40, 'The Guardian', 'https://www.theguardian.com/us', 2); 
-- INSERT INTO NewsSource VALUES (41, 'The Hill', 'https://thehill.com/', 3); 
-- INSERT INTO NewsSource VALUES (42, 'The Intercept', 'https://theintercept.com/', 1); 
-- INSERT INTO NewsSource VALUES (43, 'The New Yorker', 'https://www.newyorker.com/', 1);
-- INSERT INTO NewsSource VALUES (44, 'TheBlaze.com', 'https://www.theblaze.com/', 5); 
-- INSERT INTO NewsSource VALUES (45, 'Time Magazine', 'https://time.com/', 2); 
-- INSERT INTO NewsSource VALUES (46, 'USA TODAY', 'https://www.usatoday.com/', 2); 
-- INSERT INTO NewsSource VALUES (47, 'Vox', 'https://www.vox.com/', 1); 
-- INSERT INTO NewsSource VALUES (48, 'Wall Street Journal', 'https://www.wsj.com/', 3); 
-- INSERT INTO NewsSource VALUES (49, 'Wall Street Journal Opinion', 'https://www.wsj.com/news/opinion', 4); 
-- INSERT INTO NewsSource VALUES (50, 'Washington Examiner', 'https://www.washingtonexaminer.com/', 4); 
-- INSERT INTO NewsSource VALUES (51, 'Washington Post', 'https://www.washingtonpost.com/', 2); 
-- INSERT INTO NewsSource VALUES (52, 'Washington Times', 'https://www.washingtontimes.com/', 4); 
DELIMITER //
DROP PROCEDURE IF EXISTS AddArticle;
//
CREATE PROCEDURE AddArticle(IN AName TEXT, IN URL TEXT, IN pubDate DATETIME, IN SourceID INTEGER, IN AText TEXT, IN Summary TEXT)
	BEGIN
		DECLARE maxID INT;
        SELECT (CASE WHEN max(ArticleID) is NULL THEN 1 ELSE max(ArticleID) END) as max FROM Articles INTO maxID;
        INSERT INTO Articles VALUES (maxID + 1, AName, URL, pubDate, SourceID, AText, Summary);
    END
    //
DELIMITER //
DROP PROCEDURE IF EXISTS AssignAuthor;
//
CREATE PROCEDURE AssignAuthor(IN AuthorID INTEGER, IN ArticleID INTEGER)
	BEGIN
		INSERT INTO WroteBy VALUES(ArticleID, AuthorID);
	END
    //
DELIMITER //
DROP PROCEDURE IF EXISTS AddNewAuthor;
//
CREATE PROCEDURE AddNewAuthor(IN AName Text)
	BEGIN
		DECLARE maxID INT;
        SELECT (CASE WHEN max(AuthorID) is NULL THEN 1 ELSE max(AuthorID) END) as max FROM Author INTO maxID;
		INSERT INTO Author VALUES(maxID + 1, AName);
	END
    //
DELIMITER //
DROP PROCEDURE IF EXISTS AssignKeyWord;
//
CREATE PROCEDURE AssignKeyWord(IN ArticleID Integer, IN KeyWord TEXT)
	BEGIN
		DECLARE maxID INT;
        DECLARE keywordID INT;
        IF ((SELECT KeyWordID FROM KeyWord WHERE KeyWord.KeyWord = KeyWord) IS NOT NULL) THEN
			SELECT KeyWordID FROM KeyWord WHERE KeyWord.KeyWord = KeyWord INTO keywordID;
			IF ((SELECT KeyWordID FROM HasKeyWord WHERE HasKeyWord.ArticleID = ArticleID) != keywordID) THEN
				INSERT INTO HasKeyWord VALUES(keywordID, ArticleID);
			END IF;
        ELSE
			SELECT (CASE WHEN max(KeyWordID) is NULL THEN 1 ELSE max(KeyWordID) END) as MAX FROM KeyWord INTO maxID;
			INSERT INTO KeyWord VALUES(maxID + 1,  KeyWord);
            INSERT INTO HasKeyWord VALUES(maxID + 1, ArticleID);
        END IF;
	END
    //

