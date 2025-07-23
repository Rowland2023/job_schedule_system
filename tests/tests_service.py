import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Assuming your service.py and models.py are in the parent directory
# You might need to adjust import paths based on your exact project structure
# For example, if 'service.py' is in a 'src' folder, it might be 'from src.service import Jobs'
from service import Jobs
from models import JobModel # Assuming JobModel is in models.py

# --- Fixtures for common test data ---
@pytest.fixture
def mock_collection():
    """Mocks the MongoDB collection object."""
    return MagicMock() # MagicMock allows calling any method on it without error

@pytest.fixture
def jobs_manager(mock_collection):
    """
    Returns a Jobs instance with a mocked MongoDB collection.
    We patch MongoClient to return our mock_collection.
    """
    with patch('service.MongoClient') as MockMongoClient:
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection # Simulate db['jobs']
        MockMongoClient.return_value.__getitem__.return_value = mock_db # Simulate client['job_queue_db']
        
        manager = Jobs() # Initialize Jobs without real DB connection
        yield manager
        # Cleanup: ensure close_connection is called if it existed
        if hasattr(manager, 'close_connection'):
            manager.close_connection()

# --- Test Cases for Jobs Class ---

def test_jobs_init_creates_index(jobs_manager, mock_collection):
    """Test that the MongoDB index is created on initialization."""
    mock_collection.create_index.assert_called_once_with(
        [("priority", 1), ("estimated_time", 1), ("timestamp", 1)], background=True
    )

def test_submit_job_success(jobs_manager, mock_collection):
    """Test successful job submission."""
    job_data = {
        "priority": 1,
        "estimated_time": 30,
        "timestamp": datetime.utcnow()
    }
    jobs_manager.submit_job(job_data)
    
    # Verify that insert_one was called with the correct data
    mock_collection.insert_one.assert_called_once()
    inserted_doc = mock_collection.insert_one.call_args[0][0]
    assert inserted_doc['priority'] == job_data['priority']
    assert inserted_doc['estimated_time'] == job_data['estimated_time']
    assert inserted_doc['timestamp'] == job_data['timestamp']

def test_submit_job_missing_fields(jobs_manager):
    """Test job submission with missing required fields."""
    invalid_job_data = {
        "priority": 1,
        # 'estimated_time' is missing
        "timestamp": datetime.utcnow()
    }
    with pytest.raises(ValueError, match="Missing required fields: estimated_time"):
        jobs_manager.submit_job(invalid_job_data)

def test_next_job_empty_queue(jobs_manager, mock_collection):
    """Test retrieving next job when the queue is empty."""
    mock_collection.find_one_and_delete.return_value = None # Simulate no job found
    result = jobs_manager.next_job()
    assert result is None
    mock_collection.find_one_and_delete.assert_called_once()

def test_next_job_retrieves_correct_priority(jobs_manager, mock_collection):
    """Test that next_job retrieves the highest priority job."""
    # Simulate MongoDB returning a job
    mock_job = {
        "_id": "abc",
        "priority": 1,
        "estimated_time": 10,
        "timestamp": datetime.utcnow()
    }
    mock_collection.find_one_and_delete.return_value = mock_job
    
    result = jobs_manager.next_job()
    assert result == mock_job
    
    # Verify find_one_and_delete was called with the correct sorting
    mock_collection.find_one_and_delete.assert_called_once_with(
        filter={},
        sort=[
            ("priority", 1),
            ("estimated_time", 1),
            ("timestamp", 1)
        ]
    )

def test_next_job_removes_job_atomically(jobs_manager, mock_collection):
    """Test that find_one_and_delete is used for atomic removal."""
    # This is implicitly tested by checking find_one_and_delete is called.
    # The MagicMock ensures that the method is called, and its nature implies atomicity.
    mock_collection.find_one_and_delete.return_value = {"_id": "test_id", "priority": 1}
    jobs_manager.next_job()
    mock_collection.find_one_and_delete.assert_called_once()

# You can add more tests for specific sorting scenarios if needed,
# e.g., jobs with same priority but different estimated_time, etc.