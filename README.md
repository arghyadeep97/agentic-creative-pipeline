# Schema-Governed Creative Automation Pipeline

A full-stack, stage-gated agentic workflow designed to automate complex prompt engineering and enforce strict brand consistency without requiring model fine-tuning. 

## 🚀 Overview
This application serves as an "Agentic Creative Director," guiding users through a strict 3-step consultation pipeline to generate high-fidelity image prompts, text hooks, and anchor comments. It utilizes a local LLM environment to ensure complete data privacy and zero API costs during the drafting phase.

## ⚙️ Core Architecture & Features
* **Stage-Gated Agentic Pipeline:** Enforces a structured 3-step LLM output via a schema-locked prompt architecture.
* **Silent System-Directive Injection:** Dynamically manages conversational state and prevents LLM hallucination/brand deviation by injecting hidden system guardrails into user turns.
* **Responsive Custom Frontend:** Built with Vanilla JS, featuring asynchronous API routing and custom Regex-based markdown highlighting for optimal user experience.
* **Local Inference:** Fully integrated with LM Studio to run optimized quantized models locally.

## 🛠️ Tech Stack
* **Backend:** Python, Flask, OpenAI SDK
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **AI/LLM:** Local LLM via LM Studio (Optimized for `google/gemma-3-4b`)

## 💻 Local Setup Instructions
1. Clone the repository:
   ```bash
   git clone [https://github.com/arghyadeep97/agentic-creative-pipeline.git](https://github.com/arghyadeep97/agentic-creative-pipeline.git)
   
2. Install dependencies:
   pip install flask openai
   
3. Start your local LLM server:
   Open LM Studio and load your preferred model (e.g., Gemma 3 4B).
   Start the Local Server on port 1234.

4. Run the application:
   python app.py
   
5. Open your browser and navigate to http://127.0.0.1:5000
