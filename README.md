# Personal Learning & Research Multi-Agent Assistant

A multi-agent AI assistant for personalized learning and scientific research.

## Project Goals

The system helps students:

- interact with their course documents;
- ask questions using RAG;
- generate quizzes;
- evaluate their answers;
- create adaptive study plans;
- search scientific resources;
- compare research papers.

## Technologies

- Python
- LangChain
- LangGraph
- Ollama Cloud
- Docling
- FAISS
- Pydantic
- Streamlit

## Architecture

The project uses a Supervisor-based multi-agent architecture.

The Supervisor orchestrates specialized agents such as:

- Tutor Agent
- Quiz Agent
- Evaluation Agent
- Planner Agent
- Research Agent
- Comparison Agent

The project also integrates:

- RAG
- Middleware
- Guardrails
- Checkpoints / Memory
- Human-in-the-loop