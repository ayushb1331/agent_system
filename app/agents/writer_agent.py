import json
import asyncio
from app.core.base_agent import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self):
        # Listen for tasks on 'queue_writer'
        super().__init__(agent_name="Writer", queue_name="queue_writer")

    async def process_task(self, data: dict):
        task_id = data.get("task_id")
        context = data.get("context", "No background data provided.")
        step_description = data.get("description")

        prompt = f"""
        ACT AS: A Professional Technical Writer.
        BACKGROUND DATA: {context}
        FINAL INSTRUCTION: {step_description}
        
        Using the background data provided, write a high-quality final response.
        Ensure it is well-formatted, clear, and addresses the user's original goal perfectly.
        """

        final_output = await self.call_gemini(prompt)
        
        await self.redis.rpush("queue_results", json.dumps({
            "task_id": task_id,
            "origin": "writer",
            "status": "completed",
            "data": final_output
        }))
        print(f"[Writer] Final synthesis complete for {task_id}")

if __name__ == "__main__":
    agent = WriterAgent()
    asyncio.run(agent.listen())