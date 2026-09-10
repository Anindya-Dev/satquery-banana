import time
from backend.app.workers.job_queue import JobManager

def sample_task(x: int, y: int) -> int:
    time.sleep(0.1)
    return x + y

def test_job_queue_async_execution():
    manager = JobManager()
    job_id = manager.submit_job("SampleTask", sample_task, 10, 20)
    assert job_id.startswith("JOB-")
    
    # Wait for completion
    time.sleep(0.5)
    status = manager.get_job_status(job_id)
    assert status is not None
    assert status["status"] == "COMPLETED"
    assert status["result"]["output"] == "30"
