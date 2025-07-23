# service.py

from pymongo import MongoClient
from models import JobModel

class Jobs:
    def __init__(self, uri="mongodb://localhost:27017", db_name="job_queue_db", collection_name="jobs"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.collection.create_index([("priority", 1), ("timestamp", 1)])

    def submit_job(self, job_data):
        job = JobModel(**job_data)
        self.collection.insert_one(job.to_dict())

    def next_job(self):
        job = self.collection.find_one_and_delete(
            filter={},
            sort=[("priority", 1), ("timestamp", 1)]
        )
        return job
