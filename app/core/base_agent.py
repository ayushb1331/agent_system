import json
import asyncio
import aiohttp
from app.core.redis_client import redis_manager
from app.core.config import settings

class BaseAgent:
    def __init__(self, agent_name: str, queue_name: str):
        self.agent_name = agent_name
        self.queue_name = queue_name
        self.redis = redis_manager.get_client()
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"

    async def call_gemini(self, prompt: str) -> str:
        """Mocks the response if MOCK_MODE is True, else calls Gemini."""
        if getattr(settings, "MOCK_MODE", True): # Default to True for safety
            await asyncio.sleep(0.5)
            if "Planner" in self.agent_name:
                return json.dumps({
                    "task_id": "test-task",
                    "steps": [
                        {"step": 1, "agent": "retriever", "description": "Gathering fake data"},
                        {"step": 2, "agent": "writer", "description": "Writing fake report"}
                    ]
                })
            return f"Mocked response from {self.agent_name}"
        
        # Real API logic would go here
        return "Real API logic not triggered in Mock Mode"

    async def listen(self):
        """This is the method Python says is missing. Ensure it is indented correctly!"""
        print(f"Agent {self.agent_name} is listening on {self.queue_name}...")
        while True:
            try:
                task_data = await self.redis.blpop(self.queue_name, timeout=1)
                if task_data:
                    _, message = task_data
                    data = json.loads(message)
                    print(f"[{self.agent_name}] Received task: {data.get('task_id')}")
                    await self.process_task(data)
            except Exception as e:
                print(f"[{self.agent_name}] Error in listen loop: {e}")
            await asyncio.sleep(0.1)

    async def process_task(self, data: dict):
        raise NotImplementedError