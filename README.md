# 🌙 Sleep AI — Personalized Sleep Analysis

An AI-powered sleep health application that analyzes your Apple Health data
and generates personalized, evidence-backed recommendations using RAG
(Retrieval-Augmented Generation).

## Live Demo

https://sleep-ai-88uhbuy2uswxy43mvmv6rb.streamlit.app/

## Features

- Upload your Apple Health export zip directly
- Interactive dashboard: sleep duration, stages (REM/Deep/Core), HRV, resting HR
- AI analysis grounded in sleep science research documents
- Personalized recommendations citing your actual sleep numbers
- Free-form sleep Q&A with out-of-scope detection

## Tech Stack

- **Frontend:** Streamlit
- **AI/RAG:** LlamaIndex, Groq (LLaMA 3.3 70B), sentence-transformers
- **Vector Store:** ChromaDB
- **Data:** Apple HealthKit XML parsing, Pandas
- **Visualization:** Plotly

## How to Run Locally

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Add your Groq API key to `.env`: `GROQ_API_KEY=your_key`
5. Run: `python -m streamlit run app.py`
6. Export Apple Health data from iPhone → Health app → profile → Export All Health Data
7. Upload the zip file in the app

## Data Privacy

Your health data is processed in memory and never stored or transmitted.
