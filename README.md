# 🧠 Agentic AI System for Multi-Step Tasks

An end-to-end **agentic AI system** that decomposes complex user tasks into multiple steps and coordinates specialized agents using **async pipelines** and **Redis-based message queues**.

This project demonstrates **agent boundaries, orchestration, streaming responses, failure handling, and scalability**, strictly aligned with typical agentic-system assignment requirements.

---

## 📌 Problem Statement

Design and implement an **Agentic AI System** capable of:

- Accepting a complex user task  
- Breaking it into multiple steps  
- Assigning steps to specialized agents  
- Coordinating execution asynchronously  
- Streaming partial responses to the client  
- Handling retries, failures, and scalability concerns  

---

## 🧩 System Overview

### High-Level Flow

```
Client (FastAPI)
   |
   v
Orchestrator
   |
   v
Task Planner Agent
   |
   v
Redis Queue (step-wise routing)
   |
   +--> Retriever Agent
   +--> Analyzer Agent
   +--> Writer Agent
   |
   v
Final Result → Streamed to Client
```

---

## 🤖 Agents Implemented

| Agent | Responsibility |
|-----|---------------|
| Task Planner | Decomposes user input into ordered steps |
| Retriever | Gathers factual / contextual information |
| Analyzer | Performs reasoning and analysis |
| Writer | Produces final structured output |
| Orchestrator | Routes tasks, manages state, handles failures |

Each agent:

- Runs independently  
- Consumes tasks from Redis  
- Publishes results back to Redis  
- Uses async processing  

---

## 🧱 Architecture Decisions

### Why Agent-Based?
- Clear separation of concerns  
- Horizontal scalability  
- Easier debugging and observability  

### Why Redis?
- Lightweight message queue  
- Async-friendly  
- Easy local + cloud deployment  
- Supports pub/sub and task queues  

### Why Async (asyncio)?
- Non-blocking I/O  
- Concurrent agent execution  
- Scalable orchestration  

---

## 📂 Project Structure

```
agentic_system/
├── app/
│   ├── agents/
│   │   ├── planner_agent.py
│   │   ├── retriever_agent.py
│   │   ├── analyzer_agent.py
│   │   └── writer_agent.py
│   ├── core/
│   │   ├── base_agent.py
│   │   ├── redis_client.py
│   │   └── config.py
│   ├── orchestrator.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🔁 Async Orchestration Flow

1. Client submits a task via API  
2. Orchestrator sends task to Planner  
3. Planner returns structured steps  
4. Orchestrator dispatches each step to the correct agent  
5. Agents return results asynchronously  
6. Results are streamed to client using Server-Sent Events  
7. Final output is stored and returned  

---

## 🔄 Streaming Responses

- Implemented using **FastAPI + Server-Sent Events (SSE)**
- Client receives:
  - Processing updates  
  - Final completed result  

This keeps long-running tasks responsive.

---

## 🧪 Mock Mode vs Real Gemini API

### Why Mock Mode Exists
Due to Gemini free-tier quota exhaustion, the system supports a **Mock Mode** to:

- Demonstrate full orchestration  
- Validate agent communication  
- Show streaming and retries  
- Enable reliable live demo during evaluation  

### Mock Mode (Default)
```
MOCK_MODE=true
```

### Switching to Gemini API
```
MOCK_MODE=false
GEMINI_API_KEY=your_api_key_here
```

> No code changes required — only `.env` update.

---

## 🚀 Running the System

### 1️⃣ Start Redis
```
docker run -d -p 6379:6379 redis:7
```

### 2️⃣ Start Agents (separate terminals)
```
python -m app.agents.planner_agent
python -m app.agents.retriever_agent
python -m app.agents.analyzer_agent
python -m app.agents.writer_agent
```

### 3️⃣ Start Orchestrator
```
python -m app.orchestrator
```

### 4️⃣ Start API
```
uvicorn app.main:app --reload
```

---

## 📡 API Usage

### Submit Task
```
POST /task
{
  "user_input": "Research 2026 solid-state battery technology and summarize for investors"
}
```

### Stream Results
```
GET /stream/{task_id}
```

---

## ⚠️ Failure Handling

- Agent-level failure propagation  
- Retry logic with exponential backoff  
- Graceful task termination  
- Final error streamed to client  

---

## 📈 Scalability Considerations

- Stateless agents  
- Redis-based task routing  
- Horizontal scaling via multiple agent instances  
- Clear agent boundaries  

---

## 📝 Post-Mortem Summary

### Scaling Issue Encountered
- Gemini API free-tier rate limits caused planner failures  

### Design Decision
- Introduced request batching + shared embedding cache  

### Trade-offs Made
- Mock Mode used for demo stability  
- Redis chosen over Kafka for simplicity  

---

✅ **This project showcases real-world agentic AI system design with orchestration, async execution, and streaming.**
