from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://mongodb:27017/")
db = client["test_database"]
collection = db["test_collection"]

# Insert data

for i in range(10):
    data = {"name": "John Doe", "age": 30, "city": "New York"}
    result = collection.insert_one(data)