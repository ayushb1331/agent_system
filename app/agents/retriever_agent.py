import json
import asyncio
from app.core.base_agent import BaseAgent

class RetrieverAgent(BaseAgent):
    def __init__(self):
        # Listen for tasks on 'queue_retriever'
        super().__init__(agent_name="Retriever", queue_name="queue_retriever")

    async def process_task(self, data: dict):
        task_id = data.get("task_id")
        step_description = data.get("description")

        # Instruction for the model to act as a search/retrieval engine
        prompt = f"""
        ACT AS: A Research & Retrieval Agent.
        TASK: {step_description}
        
        Provide a detailed collection of facts, data points, or context related to the task.
        Focus on accuracy and raw information.
        """

        # 1. Call Gemini via REST
        retrieved_info = await self.call_gemini(prompt)
        
        # 2. Publish results to the central orchestrator queue
        await self.redis.rpush("queue_results", json.dumps({
            "task_id": task_id,
            "origin": "retriever",
            "status": "completed",
            "data": retrieved_info
        }))
        print(f"[Retriever] Data gathered for {task_id}")

if __name__ == "__main__":
    agent = RetrieverAgent()
    asyncio.run(agent.listen())