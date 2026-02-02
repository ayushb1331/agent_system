import json
import asyncio
from app.core.redis_client import redis_manager

class Orchestrator:
    def __init__(self):
        self.redis = redis_manager.get_client()
        self.states = {} # In-memory state tracking

    async def start_task(self, task_id: str, user_input: str):
        """Initializes a task by sending it to the Planner."""
        initial_payload = {"task_id": task_id, "user_input": user_input}
        await self.redis.rpush("queue_planner", json.dumps(initial_payload))
        print(f"[Orchestrator] Task {task_id} sent to Planner.")

    async def run(self):
        """Main loop to route tasks between agents."""
        print("Orchestrator is running...")
        while True:
            result = await self.redis.blpop("queue_results", timeout=1)
            if result:
                _, message = result
                try:
                    data = json.loads(message)
                    await self.handle_agent_response(data)
                except Exception as e:
                    print(f"[Orchestrator] Critical error processing message: {e}")
            await asyncio.sleep(0.1)

    async def handle_agent_response(self, data: dict):
        task_id = data.get("task_id")
        origin = data.get("origin")
        status = data.get("status")
        payload = data.get("data")

        # 1. Check for explicit failure status from any agent
        if status == "failed":
            error_msg = data.get("error", "Unknown agent error")
            print(f"[Orchestrator] Task {task_id} FAILED at {origin} stage: {error_msg}")
            await self.redis.set(f"final_{task_id}", f"ERROR: System failed at {origin}. Details: {error_msg}")
            return

        # 2. Handle Planner Response
        if origin == "planner":
            # Safety check: ensure payload is a dict and contains 'steps'
            if not isinstance(payload, dict) or "steps" not in payload:
                print(f"[Orchestrator] Planner sent invalid payload for {task_id}: {payload}")
                await self.redis.set(f"final_{task_id}", "ERROR: Planner failed to generate a valid task sequence.")
                return

            steps = payload.get("steps", [])
            self.states[task_id] = {"steps": steps, "current_step_idx": 0, "results": []}
            await self.dispatch_next_step(task_id)

        # 3. Handle Worker Responses (Retriever, Analyzer, Writer)
        else:
            if task_id not in self.states:
                print(f"[Orchestrator] Received response for unknown/expired task {task_id}")
                return

            print(f"[Orchestrator] Agent {origin} finished for {task_id}")
            # Ensure payload is a string or serializable data
            self.states[task_id]["results"].append(str(payload))
            self.states[task_id]["current_step_idx"] += 1
            await self.dispatch_next_step(task_id)

    async def dispatch_next_step(self, task_id: str):
        state = self.states.get(task_id)
        idx = state["current_step_idx"]
        steps = state["steps"]

        if idx < len(steps):
            current_step = steps[idx]
            target_agent = current_step.get("agent")
            
            dispatch_data = {
                "task_id": task_id,
                "description": current_step.get("description", "No description provided"),
                "context": "\n---\n".join(state["results"])
            }
            
            queue_name = f"queue_{target_agent}"
            await self.redis.rpush(queue_name, json.dumps(dispatch_data))
            print(f"[Orchestrator] Dispatched step {idx+1}/{len(steps)} to {target_agent}")
        else:
            # Task complete!
            final_result = state["results"][-1] if state["results"] else "No output generated."
            await self.redis.set(f"final_{task_id}", final_result)
            print(f"[Orchestrator] Task {task_id} is COMPLETE.")
            # Clean up in-memory state
            del self.states[task_id]

if __name__ == "__main__":
    orch = Orchestrator()
    asyncio.run(orch.run())