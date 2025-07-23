# models.py

from datetime import datetime

class JobModel:
    def __init__(self, priority, estimated_time, timestamp=None):
        self.priority = priority
        self.estimated_time = estimated_time
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        return {
            "priority": self.priority,
            "estimated_time": self.estimated_time,
            "timestamp": self.timestamp
        }
