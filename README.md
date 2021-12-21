# Final Project for Databases (601.615)

### How to run this code

To run this code for the first time, you must have Node.js and Python 3.9 installed. To install Node.js, please visit [this link](https://nodejs.org/en/download/). To download Python 3.9, please visit [this link](https://www.python.org/downloads/).

Once you have those two things, clone this repository in any folder by typing `git clone https://github.com/agking10/IR_FinalProject.git` from the command line.

Next, navigate to this folder by typing `cd IR_FinalProject`. Type `git checkout process-query`.

To create a virtual environment, type `python -m venv venv` and then type `source ./venv/bin/activate`.

To install the required python packages, use the command `pip3 install -r requirements.txt`.

You may need to download the `stopwords` NLTK resource if not already downloaded. If this is indeed the case, a `LookupError` will occur when initializing the database and instructions on how to use the NLTK Downloader to obtain this resource will be printed to the console.

Now, everything is set up to run the REST API. To start the server, run the command `python backend/api.py --reset_db --reset_cache`. This may take a few seconds to start because the script needs to vectorize the documents in the database. If you have run the script in the past and know that the databases are populated, you can avoid recreating the document vectors by removing the flags `--reset_db` and `--reset_cache`.

Once the backend is running, open another terminal and navigate to the project root folder (`IR_FinalProject`), then navigate to the webpage folder with `cd webpage`.

First, `yarn` must be installed. You can do so by running the command `npm install --global yarn`. Then, you may need to run `yarn add reactstrap`. After that, `yarn build` should make a production build. Once this completes, you can install the additional required packages by typing `npm install` into the command line. Once all of these packages are installed, typing the command `npm start` should automatically open up the application using a development server allowed you to play around with the application.

#### A demo of this application is available [here](https://youtu.be/Xso2Z3c4dII)

![](./screenshots/NewsLine1.PNG)

![](./screenshots/NewsLine2.png)

There were 432 news source candidates in the original dump from AllSides Media Bias Ratings, but only 358 news sources
were actually valid. The [source stub](media_bias_table.html) was saved from
[here](https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B2%5D=2&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=)
on May 6, 2021. We scraped 39,278 stories, which can be found in Pickle format [here](stories.pickle).

For this project, we decided to host the website remotely. NewsLine is hosted at 44.202.10.14:3000. To access it, please go to
[http://44.202.10.14:3000](http://44.202.10.14:3000).
The schema used for this database is found in the file `DatabaseFinalProject.sql`. The script used to normalize and upload
the scraped and indexed article data is `db/load_db.py`.
