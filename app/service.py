# service.py

from pymongo import MongoClient
from models import JobModel

class Jobs:
    def __init__(self, uri="mongodb://localhost:27017", db_name="job_queue_db", collection_name="jobs"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # --- UPDATE THIS LINE ---
        self.collection.create_index([("priority", 1), ("estimated_time", 1), ("timestamp", 1)], background=True)
        # --- END OF UPDATE ---

    def submit_job(self, job_data):
        required = ['priority', 'estimated_time', 'timestamp']
        missing = [k for k in required if k not in job_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        job = JobModel(**job_data)
        self.collection.insert_one(job.to_dict())


    def next_job(self):
        job = self.collection.find_one_and_delete(
            filter={},
            sort=[
                ("priority", 1),        # Highest priority first
                ("estimated_time", 1),  # Then shortest estimated time
                ("timestamp", 1)        # Then earliest submission
            ]
        )
        return job