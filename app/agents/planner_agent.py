import json
import asyncio
from app.core.base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self):
        # Inherit correctly from BaseAgent
        super().__init__(agent_name="TaskPlanner", queue_name="queue_planner")

    async def process_task(self, data: dict):
        task_id = data.get("task_id")
        user_input = data.get("user_input")

        # Get response (Mock or Real)
        raw_response = await self.call_gemini(f"Plan for: {user_input}")
        
        # Clean and Publish
        cleaned_json = raw_response.replace("```json", "").replace("```", "").strip()
        try:
            plan = json.loads(cleaned_json)
            await self.redis.rpush("queue_results", json.dumps({
                "task_id": task_id,
                "origin": "planner",
                "status": "completed",
                "data": plan
            }))
            print(f"[Planner] Dispatched plan for {task_id}")
        except Exception as e:
            print(f"[Planner] JSON Error: {e}")

if __name__ == "__main__":
    # This will now work because 'listen' exists in the parent BaseAgent
    agent = PlannerAgent()
    asyncio.run(agent.listen())