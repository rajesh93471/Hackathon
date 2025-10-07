
# Web-Navigator-AI-Agent 🌐

![Project Status](https://img.shields.io/badge/status-Prototype-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-blue)
![Playwright](https://img.shields.io/badge/Playwright-Automation-blue)
![Ollama](https://img.shields.io/badge/LLM-Ollama-blue)

---


## 📌 Problem Statement
In today’s digital world, humans interact with hundreds of websites daily. Imagine an intelligent assistant that can autonomously browse, extract data, and perform web tasks — **without depending on cloud-based LLMs**.

The **Web Navigator AI Agent** addresses this challenge by combining:  
- **Local LLM** → for instruction understanding  
- **Browser automation** → for execution of tasks  
- **Structured outputs** → for actionable insights  

---

## 💡 Proposal & Prototype Plan
Our goal is to build a fully local AI agent that can process natural language commands and perform web tasks autonomously. The prototype includes:  

1. **Instruction Parsing** – Local LLaMA 3.2 7B interprets user commands.  
2. **Browser Automation** – Playwright executes actions in a headless or VM browser.  
3. **Task Execution** – Multi-step reasoning and error handling.  
4. **Output Generation** – Structured JSON/CSV results, optional screenshots.  
5. **User Interaction** – React web interface for visualization, with optional voice commands.  

This modular approach ensures scalability and maintainability, separating LLM logic, backend automation, and frontend display.

---

## 💡 How We Worked
Our approach was **iterative and collaborative**:

1. **Research & Design** – Studied user needs, AI agent patterns, and browser automation frameworks.  
2. **Prototype Development** – Started with Flask + Playwright backend, then integrated Ollama for local LLM reasoning.  
3. **Frontend Integration** – Built React UI for smooth interaction and structured result visualization.  
4. **Testing & Refinement** – Debugged automation flows, refined prompts, and ensured local deployment worked seamlessly.  
5. **Collaboration** – Each member specialized in modules (backend, frontend, LLM fine-tuning, orchestration).  

This workflow ensured a fully functional end-to-end prototype within the project timeline.

---

## 💡 Workflow
The Web Navigator AI Agent processes a user instruction as follows:  

1. **Instruction Parsing** → Local LLaMA interprets commands.  
2. **Browser Automation** → Playwright executes actions in headless/VM browser.  
3. **Task Execution** → Supports multi-step reasoning & error handling.  
4. **Output Generation** → JSON/CSV structured results with optional screenshots.  
5. **User Interaction** → React GUI + optional voice commands.  

---

## ✅ Current Features

| Feature              | Description                               | Status |
|----------------------|-------------------------------------------|--------|
| Instruction Parsing   | Understands natural language via local LLM | ✅ |
| Browser Automation    | Search, click, form fill, scrape          | ✅ |
| Multi-step Reasoning  | Execute chained commands intelligently    | ⚡ Planned |
| Task Memory           | Remembers previous instructions           | ⚡ Planned |
| Error Handling        | Retry and fallback strategies             | ⚡ Planned |
| Structured Output     | JSON/CSV with optional screenshots        | ✅ |
| GUI Interface         | React web app for interaction             | ✅ |
| Voice Input           | Speech-to-command capability              | ⚡ Planned |

---

## 🛠 Tech Stack

- **Frontend:** React + Vite  
- **Backend:** Python + Flask  
- **Automation:** Playwright  
- **LLM:** Ollama LLaMA 3.2 7B  
- **Interface:** REST API + Web UI  
- **Deployment:** Local, no cloud dependency  

---

## 👥 Team Contributions

| Member        | Role              | Contribution |
|---------------|------------------|--------------|
| **Rawhan Ramzi** | Project Lead / LLM Specialist  | Vision, LLM orchestration, architecture & roadmap |
| **Sumanth**      | Backend Developer | Flask API, Playwright integration, data extraction |
| **Harish**       | Frontend Developer | React UI, structured result display |
| **Rajesh**       | LLM Specialist  / Frontend Developer | Configured and fine-tuned local LLaMA model |

---

## 📈 Vision
The Web Navigator AI Agent is a **foundation for next-generation personal web assistants**.  
Future goals include:  
- Multi-agent collaboration  
- Adaptive learning from user behavior  
- Integration with local databases for enhanced memory  
- Cross-platform desktop version  

---

## ⚡ Getting Started

### 🔧 Backend Setup
Run the following commands to set up and start the backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
🎨 Frontend Setup
Run the following commands to set up and start the frontend:
```bash
cd frontend
npm install
npm run dev
```

## 🎥 Video Explanation

Watch the Video explanation of the Web Navigator AI Agent here:

👉 [click here](https://drive.google.com/file/d/1HHtUMJBIXakTRT8gCqP4Ruiy4otmqbES/view?usp=sharing)

## 📂 Repository Structure

The repository is organized as follows:
```bash 
Web-Navigator-AI-Agent/
├── backend/        # Flask + Playwright backend
├── frontend/       # React frontend
├── docs/           # Diagrams, screenshots, architecture
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .env.example
└── .gitignore
```

