from fastapi import FastAPI
from loader import BatchLoader
from queue_service import BatchProcessor
from dotenv import load_dotenv


app = FastAPI(title="AIPES API", version="1.0.0")

loader = BatchLoader(source_config="test_ppts")
queue = BatchProcessor(concurrency_limit=3) 

@app.get("/test_pipeline")
async def test_pipeline():
    files = loader.fetch_files()
    
    if not files:
        return {"message": "No PDFs found in 'test_ppts' folder."}
        
    print(f"[AIPES] Queuing {len(files)} files for evaluation...")
    
    results = await queue.process_queue(files)
    
    return {
        "status": "Success",
        "total_evaluated": len(results),
        "results": results
    }