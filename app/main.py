import asyncio
import json
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.core.redis_client import redis_manager
from app.orchestrator import Orchestrator

app = FastAPI(title="Agentic AI System")
orchestrator = Orchestrator()

@app.post("/task")
async def create_task(user_input: str, background_tasks: BackgroundTasks):
    """
    Submits a task to the system.
    Returns a task_id immediately.
    """
    task_id = str(uuid.uuid4())
    
    # Start the orchestration in the background
    background_tasks.add_task(orchestrator.start_task, task_id, user_input)
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/stream/{task_id}")
async def stream_task_updates(task_id: str):
    """
    Streams updates from Redis to the client using SSE.
    """
    async def event_generator():
        redis = redis_manager.get_client()
        print(f"Streaming started for {task_id}")
        
        while True:
            # 1. Check if the final result exists
            final_data = await redis.get(f"final_{task_id}")
            if final_data:
                yield f"data: {json.dumps({'status': 'completed', 'result': final_data})}\n\n"
                break
            
            # 2. Check for intermediate progress (optional: we could add a progress queue)
            # For now, we heartbeat to keep the connection alive
            yield f"data: {json.dumps({'status': 'processing'})}\n\n"
            
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)