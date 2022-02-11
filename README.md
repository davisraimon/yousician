
## Installation
First make sure Docker is installed in your system. if not, complete the installation process for Docker from given link.
https://docs.docker.com/desktop/windows/install/
Once Docker is installed, execute the below command to run the mongodb container

```sh
docker run --detach --name songs_db --publish 127.0.0.1:27016:27017 mongo:4.4
```
Once Mongo container is up and running, we can start the flask server.
Go to the yousician folder and install the required packages.
Then start the flask server using flask run command.
```sh
cd yousician
pip install requirements.txt
python -m flask run
```
Mongo DB would not have any initial data for testing. To insert initial records, hit
http://127.0.0.1:5000/injectsampledata
The above route will create the DB and collection if not present and reset the data to the ones present in /yousician/db/dbsampledata.json file.

To execute the testcases, go to yousician folder and execute below commands
```sh
cd yousician
python -m unittest test.py
```
## REST APIs
##### 1) Fetch API [GET]
- http://127.0.0.1:5000/fetch/{page}
- For fetching data from the songs collection
- Accepts page as a param
- Returns data, total_count, next_page, prev_page, current_page
- Note : if prev_page or next_page is -1, then respective pagination is not possible
##### 2) Search API [GET]
- http://127.0.0.1:5000/search/{search}
- For searching in artist & title field
- Accepts url param search (mandatory)
- Returns the data as array of objects
- Note : If search param is empty, [] will be returned as reponse
##### 3) Average Difficulty [GET]
- http://127.0.0.1:5000/average_difficulty/{level}
- For calculating Average Difficulty from the songs collection
- Accepts optional url param level
- Returns average
##### 4) Add Ratings [POST]
- http://127.0.0.1:5000/addratings/{song_id}  (form data example = {"ratings": 4.6})
- For adding ratings to a particular song
- Accept params song_id & ratings
- Returns response message
- Note : if invalid ratings or song_id, returns 401 status code with error message
##### 5) Get Ratings [GET]
- http://127.0.0.1:5000/getratings/{song_id}
- For getting average,maximum and mininum ratings to a particular song
- Accept params song_id
- Returns response with average_ratings, max_ratings, min_ratings
- Note : if empty ratings or invalid song_id, returns 401 status code with error message
