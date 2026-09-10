import asyncio
import uuid
import threading
from typing import Dict, Any, Callable, Optional
from backend.app.storage.metadata_db import MetadataDB
from backend.app.core.logging import logger

class JobManager:
    def __init__(self, metadata_db: Optional[MetadataDB] = None):
        self.db = metadata_db or MetadataDB()

    def submit_job(self, task_type: str, func: Callable, *args, **kwargs) -> str:
        """
        Submits a long-running function to execute asynchronously in a background thread.
        Returns job_id string immediately.
        """
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        self.db.create_job(job_id=job_id, task_type=task_type)

        thread = threading.Thread(
            target=self._run_job_wrapper,
            args=(job_id, func, args, kwargs),
            daemon=True
        )
        thread.start()
        return job_id

    def _run_job_wrapper(self, job_id: str, func: Callable, args: tuple, kwargs: dict):
        try:
            self.db.update_job(job_id=job_id, status="RUNNING", progress_pct=10.0)
            result = func(*args, **kwargs)
            
            # If Pydantic model, convert to dict
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            elif hasattr(result, "dict"):
                result_dict = result.dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {"output": str(result)}

            self.db.update_job(job_id=job_id, status="COMPLETED", progress_pct=100.0, result=result_dict)
            logger.info("Background job completed successfully.", job_id=job_id)
        except Exception as e:
            err_msg = str(e)
            logger.error("Background job execution failed.", job_id=job_id, error=err_msg)
            self.db.update_job(job_id=job_id, status="FAILED", progress_pct=0.0, error_msg=err_msg)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_job(job_id)

job_manager = JobManager()
