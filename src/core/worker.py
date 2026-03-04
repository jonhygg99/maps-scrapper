"""
Multi-threaded Worker for Scraping Tasks
Handles asynchronous scraping operations with thread safety
"""
import threading
import queue
import asyncio
from typing import Callable, Any, Optional
from src.utils.logger import Logger


class ScraperWorker(threading.Thread):
    """Thread worker for executing scraping tasks"""

    def __init__(
        self,
        worker_id: int,
        task_queue: queue.Queue,
        result_queue: queue.Queue,
        scraper_func: Callable,
        **kwargs
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.scraper_func = scraper_func
        self.kwargs = kwargs
        self._stop_event = threading.Event()
        self.logger = Logger.get_logger(f"Worker-{worker_id}")

    def run(self):
        self.logger.info(f"Worker {self.worker_id} started")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._async_run())
        except Exception as e:
            self.logger.error(f"Worker {self.worker_id} error: {e}")
        finally:
            loop.close()
            self.logger.info(f"Worker {self.worker_id} stopped")

    async def _async_run(self):
        while not self._stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            if task is None:
                self.logger.info(f"Worker {self.worker_id} received stop signal")
                self.task_queue.task_done()
                break

            self.logger.info(f"Worker {self.worker_id} processing: {task}")
            try:
                result = await self.scraper_func(task, **self.kwargs)
                self.result_queue.put({
                    'status': 'success',
                    'task': task,
                    'result': result,
                    'worker_id': self.worker_id
                })
                self.logger.info(f"Worker {self.worker_id} completed: {task}")
            except Exception as e:
                self.logger.error(f"Worker {self.worker_id} error processing task: {e}")
                self.result_queue.put({
                    'status': 'error',
                    'task': task,
                    'error': str(e),
                    'worker_id': self.worker_id
                })
            finally:
                self.task_queue.task_done()

    def stop(self):
        """Signal the worker to stop"""
        self._stop_event.set()


class WorkerPool:
    """Manages a pool of worker threads"""

    def __init__(self, num_workers: int, scraper_func: Callable, **kwargs):
        self.num_workers = num_workers
        self.scraper_func = scraper_func
        self.kwargs = kwargs
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.logger = Logger.get_logger("WorkerPool")

    def start(self):
        self.logger.info(f"Starting {self.num_workers} workers")
        for i in range(self.num_workers):
            worker = ScraperWorker(
                worker_id=i,
                task_queue=self.task_queue,
                result_queue=self.result_queue,
                scraper_func=self.scraper_func,
                **self.kwargs
            )
            worker.start()
            self.workers.append(worker)

    def add_task(self, task: Any):
        self.task_queue.put(task)

    def add_tasks(self, tasks: list):
        for task in tasks:
            self.add_task(task)

    def get_result(self, timeout: Optional[float] = None) -> Optional[dict]:
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self, wait: bool = True, force: bool = False):
        self.logger.info("Stopping all workers" + (" (forced)" if force else ""))
        if force:
            for worker in self.workers:
                worker.stop()
            while not self.task_queue.empty():
                try:
                    self.task_queue.get_nowait()
                    self.task_queue.task_done()
                except queue.Empty:
                    break
            self.workers.clear()
            self.logger.info("All workers force-stopped (daemon threads)")
            return

        # Graceful stop: send poison pills
        for _ in range(self.num_workers):
            self.task_queue.put(None)
        for worker in self.workers:
            worker.stop()
        if wait:
            for worker in self.workers:
                worker.join(timeout=5)
        self.workers.clear()
        self.logger.info("All workers stopped" + (" gracefully" if wait else ""))

    def is_active(self) -> bool:
        return any(worker.is_alive() for worker in self.workers)

    def tasks_pending(self) -> int:
        return self.task_queue.qsize()

    def results_available(self) -> int:
        return self.result_queue.qsize()
