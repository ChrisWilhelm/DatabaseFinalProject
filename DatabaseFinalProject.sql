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

DELIMITER //
DROP PROCEDURE IF EXISTS FindSimilarKeywords;
//
CREATE PROCEDURE FindSimilarKeywords(IN word text)
BEGIN
	DECLARE wordRegex text;
    SET wordRegex = CONCAT("%", word, "%");
	SELECT H.ArticleID FROM HasKeyWord H, KeyWord K WHERE H.KeyWordID = K.KeyWordID AND K.KeyWord LIKE wordRegex;
END
//

DELIMITER //
DROP PROCEDURE IF EXISTS FindSimilarNewssource;
//
CREATE PROCEDURE FindSimilarNewssource(IN word text)
BEGIN
	DECLARE wordRegex text;
    SET wordRegex = CONCAT("%", word, "%");
	SELECT A.ArticleID FROM NewsSource N, Articles A WHERE N.NewsSourceID = A.NewsSourceID AND N.NewsSourceName LIKE wordRegex;
END
//

DROP PROCEDURE IF EXISTS FindSimilarAuthor;
//
CREATE PROCEDURE FindSimilarAuthor(IN word text)
BEGIN
	DECLARE wordRegex text;
    SET wordRegex = CONCAT("%", word, "%");
	SELECT W.ArticleID FROM WroteBy W, Author A WHERE A.AuthorID = W.AuthorID AND A.AName LIKE wordRegex;
END
//

DROP PROCEDURE IF EXISTS FindSimilarTitle;
//
CREATE PROCEDURE FindSimilarTitle(IN word text)
BEGIN
	DECLARE wordRegex text;
    SET wordRegex = CONCAT("%", word, "%");
	SELECT A.ArticleID FROM Articles A WHERE A.AName LIKE wordRegex;
END
//


