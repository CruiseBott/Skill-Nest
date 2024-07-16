from pymongo import MongoClient
import json

# Connect to MongoDB
client = MongoClient("mongodb+srv://user:user123@cluster0.z5xjddp.mongodb.net/")

# Access the database and collection containing the job data
db = client["database"]
job_data_collection = db["job_data"]

# Convert the description field to a string for all documents
job_data_collection_str = db["job_data_str"]
for doc in job_data_collection.find():
    doc_str = json.dumps(dict(doc))
    if "course_links" in doc:
        job_data_collection_str.insert_one({"_id": doc["_id"], "description": doc_str, "course_links": doc["course_links"]})
    else:
        job_data_collection_str.insert_one({"_id": doc["_id"], "description": doc_str})