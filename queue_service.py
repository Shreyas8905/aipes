import asyncio
from ai_engine import run_ai_pipeline
class BatchProcessor:
    def __init__(self, concurrency_limit: int = 3):
        self.semaphore = asyncio.Semaphore(concurrency_limit)
    async def _worker(self, file_data):
        async with self.semaphore:
            try:
                print(f"--> Processing: {file_data['team_name']}")
                result = await run_ai_pipeline(file_data)
                print(f"<-- Finished: {file_data['team_name']}")
                return result
            except Exception as e:
                print(f"!!! Error {file_data['team_name']}: {e}")
                return {"team_name": file_data["team_name"], "error": str(e)}
    async def process_queue(self, files_list):
        tasks = [self._worker(f) for f in files_list]
        return await asyncio.gather(*tasks)