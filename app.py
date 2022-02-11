from urllib import response
from flask import Flask, jsonify, make_response, request
from db.dbconnect import *
from bson.json_util import dumps
import json

myapp = Flask(__name__)


@myapp.route("/")
def home():
    return "Hello, Flask!"

# For Injecting sample data from dbsampledata.json file
@myapp.route("/injectsampledata")
def injectsampledata():
    mycol = client["songs_db"]["songs"]
    mycol.drop()
    f = open('db/dbsampledata.json')
    datatoinsert = json.load(f)
    mycol = client["songs_db"]["songs"]
    mycol.insert_many(datatoinsert)
    f.close()
    return "Sample Data from dbsampledata.json file has been updated to mongo collection songs'"


# For fetching data from the songs collection
# Accepts page as a param
# Returns data, total_count, next_page, prev_page, current_page
# Note : if prev_page or next_page is -1, then respective pagination is not possible
@myapp.route("/fetch/", defaults={'page': 0})
@myapp.route("/fetch/<page>")
def fetch(page=0):
    # filter - page
    page = int(page)
    response = {}
    mycol = client["songs_db"]["songs"]
    res = mycol.find({}, {'_id': 0}).skip(page*10).limit(10)
    count = mycol.count()
    res = [i for i in res]
    response["res"] = res
    response["total_count"] = count
    response["current_page"] = page
    response["next_page"] = page+1 if (page+1)*10 < count else -1
    response["prev_page"] = page-1 if count != 0 else -1
    return make_response(jsonify(response), 200)


# For calculating Average Difficulty from the songs collection
# Accepts optional url param level
# Returns average
@myapp.route('/average_difficulty/', defaults={'level': None})
@myapp.route("/average_difficulty/<level>")
def average_difficulty(level=None):
    match = []
    msg = "Not enough data to process the average"
    avg = "-"
    code = 401

    if level:
        match = [{"$match": {"level": int(level)}}]

    agg = [{"$group": {"_id": "_id", "AverageValue": {"$avg": "$difficulty"}}}]

    mycol = client["songs_db"]["songs"]
    res = mycol.aggregate(match+agg)
    res = json.loads(dumps(res))
    if len(res) > 0:
        avg = round(res[0]['AverageValue'], 2)
        msg = "Success"
        code = 200

    response = {"msg": msg, "average": avg}
    return make_response(jsonify(response), code)


# For searching in artist & title field
# Accepts url param search
# Returns the data as array of objects
# Note : If search param is empty, [] will be returned as reponse
@myapp.route('/search/', defaults={'search': None})
@myapp.route("/search/<search>")
def search(search=None):
    # filter - search string
    if not search:
        return make_response(jsonify({"msg": "Search Unuccessful - search keyword should be passed", "res": []}), 401)

    res = []

    mycol = client["songs_db"]["songs"]
    mycol.create_index(
        [("title", "text"), ("artist", "text")], name="songstextsearch")
    res = mycol.find({"$text": {"$search": search}})
    res = json.loads(dumps(res))

    response = {"msg": "Search Successful", "res": res}
    return make_response(jsonify(response), 200)


# For adding ratings to a particular song
# Accept params song_id & ratings
# Returns response message
# Note : if invalid ratings or song_id, returns 401 status code with error message
@myapp.route("/addratings/<song_id>", methods=['POST'])
def addratings(song_id=-1):
    # filter - song ID
    if request.method == 'POST':
        ratings_to_add = request.form['ratings']
        if ratings_to_add.isalpha() or float(ratings_to_add)<1 or float(ratings_to_add)>5: 
            return make_response(jsonify({"msg": "Invalid ratings. Only 0-5 allowed"}), 401)

        ratings_to_add = float(ratings_to_add)
        mycol = client["songs_db"]["songs"]
        res = mycol.find_one({"song_id": song_id})
        if not res:
            return make_response(jsonify({"msg": "song ID not found"}), 401)

        current_ratings_list = res["ratings"]
        updated_ratings_list = current_ratings_list + [ratings_to_add]
        mycol.find_one_and_update({"song_id": song_id}, {
                                  "$set": {"ratings": updated_ratings_list}})
    # post param - rating
    return make_response(jsonify({"msg": "Ratings for the song updated"}), 200)


# For getting average,maximum and mininum ratings to a particular song
# Accept params song_id
# Returns response with average_ratings, max_ratings, min_ratings
# Note : if empty ratings or invalid song_id, returns 401 status code with error message
@myapp.route("/getratings/", defaults={'song_id': -1})
@myapp.route("/getratings/<song_id>")
def getratings(song_id=-1):
    # filter - song ID
    mycol = client["songs_db"]["songs"]
    res = mycol.find_one({"song_id": song_id})
    if not res:
        return make_response(jsonify({"msg": "song ID not found"}), 401)
    if "ratings" not in res.keys() or len(res["ratings"]) == 0:
        return make_response(jsonify({"msg": "Ratings are not yet added to this song ID"}), 401)

    current_ratings_list = res["ratings"]
    max_ratings = max(current_ratings_list)
    min_ratings = min(current_ratings_list)
    average_ratings = round(sum(current_ratings_list) /
                            len(current_ratings_list), 2)
    res = {"msg": "Ratings for Song ID fetched succesfully"}
    res["average_ratings"] = average_ratings
    res["max_ratings"] = max_ratings
    res["min_ratings"] = min_ratings
    return make_response(jsonify(res), 200)
