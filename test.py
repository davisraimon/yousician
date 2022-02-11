from app import myapp
import unittest
import json

class FlaskTest(unittest.TestCase):
    def test_for_fetch(self):
        tester = myapp.test_client(self)
        response = tester.get("/fetch/")
        # check for 200 response
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        # check for array return
        data_length = len(json.loads(response.data)["res"])
        self.assertGreaterEqual(data_length, 1)

    def test_for_average_difficulty(self):
        tester = myapp.test_client(self)
        # average difficulty if no level is mentioned
        response = tester.get("/average_difficulty/")
        statuscode = response.status_code
        avg = json.loads(response.data)["average"]
        self.assertEqual(statuscode, 200)
        self.assertEqual(avg, 9.97)

        # average difficulty if level is mentioned and data is present
        response = tester.get("/average_difficulty/13")
        statuscode = response.status_code
        avg = json.loads(response.data)["average"]
        self.assertEqual(statuscode, 200)
        self.assertEqual(avg, 14.1)

        # average difficulty if level is mentioned and data is not present
        response = tester.get("/average_difficulty/19")
        statuscode = response.status_code
        avg = json.loads(response.data)["average"]
        self.assertEqual(statuscode, 401)
        self.assertEqual(avg, "-")

    def test_for_search(self):
        tester = myapp.test_client(self)
        search_word = "finger"
        # if search is empty, it returns 401. Ideally fetch call should be used if search is empty
        response = tester.get("/search/")
        statuscode = response.status_code
        self.assertEqual(statuscode, 401)
        # if search is present
        response = tester.get("/search/{}".format(search_word))
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        search_data = [i for i in json.loads(response.data)["res"] if search_word in i["artist"].lower() or search_word in i["title"].lower()] 
        self.assertEqual(len(search_data), len(json.loads(response.data)["res"]))

    def test_for_add_ratings(self):
        tester = myapp.test_client(self)

        # if song id is not present
        response = tester.post("/addratings/10001", data = {"ratings":3.8})
        statuscode = response.status_code
        self.assertEqual(statuscode, 401)
        
        # if song id is present
        response = tester.post("/addratings/13", data = {"ratings":3.8})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_for_get_ratings(self):
        tester = myapp.test_client(self)

        # if song id is present
        response = tester.get("/getratings/13")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

        # if song id is not present
        response = tester.get("/getratings/10001")
        statuscode = response.status_code
        self.assertEqual(statuscode, 401)

        # if song id has empty ratings
        response = tester.get("/getratings/1")
        statuscode = response.status_code
        self.assertEqual(statuscode, 401)


if __name__ == "__main__":
    unittest.main()