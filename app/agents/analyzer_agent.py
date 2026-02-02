import json
import asyncio
from app.core.base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        # Listen for tasks on 'queue_analyzer'
        super().__init__(agent_name="Analyzer", queue_name="queue_analyzer")

    async def process_task(self, data: dict):
        task_id = data.get("task_id")
        # In a real flow, 'context' would be passed from previous steps
        context_to_analyze = data.get("context", "No context provided.")
        step_description = data.get("description")

        prompt = f"""
        ACT AS: A Data Analyst.
        RAW DATA / CONTEXT: {context_to_analyze}
        INSTRUCTION: {step_description}
        
        Perform a deep-dive analysis. Identify trends, sentiment, or key takeaways.
        """

        analysis_result = await self.call_gemini(prompt)
        
        await self.redis.rpush("queue_results", json.dumps({
            "task_id": task_id,
            "origin": "analyzer",
            "status": "completed",
            "data": analysis_result
        }))
        print(f"[Analyzer] Analysis complete for {task_id}")

if __name__ == "__main__":
    agent = AnalyzerAgent()
    asyncio.run(agent.listen())