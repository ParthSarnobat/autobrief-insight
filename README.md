<div align="center">
  <h1>🔍 Autobrief Insight</h1>
  <p><b>Agentic intelligence for the modern researcher.</b></p>
  
  [![Built with Gradio](https://img.shields.io/badge/Built%20with-Gradio-orange?style=for-the-badge&logo=gradio)](https://gradio.app/)
  [![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-blue?style=for-the-badge)](https://ai.google.dev/)
  [![Hackathon Submission](https://img.shields.io/badge/Submission-Kaggle%20AI%20Agents-success?style=for-the-badge)](#)
</div>

<br/>

> **🎥 Watch the Demo:** [[Youtube](https://youtu.be/nhErVncYv-Y)]  
> **🏆 Kaggle Writeup:** [[Kaggle](https://kaggle.com/competitions/vibecoding-agents-capstone-project/writeups/autobrief-insight)]

## 🧠 The Problem & The Solution

**The Problem:** The artificial intelligence landscape moves at blinding speed. Researchers, developers, and enterprise leaders are overwhelmed by the daily flood of news. Traditional RSS feeds provide noise without context, and manual research is time-consuming. 

**The Solution:** **Autobrief Insight** is an autonomous, multi-agent intelligence dashboard that securely curates, analyzes, and allows you to interactively chat with the day's top AI news. Instead of just reading the news, you have a team of AI agents that read it, extract the deep technical insights, and answer your follow-up questions in real-time.

---

## ⚙️ System Architecture

Autobrief Insight is powered by **ADK 2.0** (Agent Development Kit) and utilizes three highly specialized agents acting in concert:

### 1. 📡 The Scout Agent (Ingestion)
Acting as the autonomous data gatherer, the Scout agent leverages an **MCP Server** integration. Without requiring user input, it autonomously polls external APIs (Google News RSS for AI), parses the XML using `requests` and `BeautifulSoup`, and extracts the top headlines, URLs, and raw text from the last 24 hours.

### 2. 🔬 The Analyst Agent (Synthesis)
The Analyst takes the raw web data from the Scout and applies rigid prompt engineering to extract high-signal technical insights. It bypasses clickbait and redundant titles, forcing the Gemini LLM to return strict JSON arrays containing 3-4 deep, unique, and actionable summary points per article.

### 3. 💬 The Interrogator Agent (Interactive Context)
Located in the "Interrogator Terminal," this conversational agent is granted shared-state memory of the Analyst's compiled report. It securely sanitizes user inputs and allows researchers to ask deep-dive follow-up questions (e.g., *"Tell me more about the technical specs of the new model mentioned in the first article."*) based directly on the day's fetched context.

<img width="2720" height="2768" alt="autobrief_insight_pipeline_flowchart" src="https://github.com/user-attachments/assets/aa1dddb7-5d5b-403e-8730-da23b0a522fb" />

---

## ✨ Key Features & UX

* **Fully Autonomous Pipeline:** A single click of the "🚀 Fetch Today's AI News" button triggers the entire multi-agent loop.
* **Premium Glassmorphic UI:** Built purely in Python using Gradio Blocks and custom injected CSS.
* **Dynamic Grid Layout:** Articles are rendered as beautifully styled, auto-scaling HTML cards with an orange-to-gold gradient theme, custom hover physics, and direct source links.
* **Seamless Chat Terminal:** The Interrogator chatbot features a borderless, floating UI design that matches modern SaaS platforms, stripping away clunky nested containers.

---

## 🛠️ Tech Stack

* **LLM Provider:** Google Gemini API (`gemini-2.5-flash` / `gemini-3.5-flash`)
* **Framework:** Python, Gradio
* **Agent Architecture:** ADK 2.0, MCP (Model Context Protocol) Server
* **Web Parsing:** `requests`, `BeautifulSoup4`
* **Styling:** Custom CSS, CSS Grid, Flexbox, embedded SVG graphics

---

## 🚀 Installation & Local Setup

**1. Clone the repository**
```bash
git clone [https://github.com/ParthSarnobat/autobrief-insight.git](https://github.com/ParthSarnobat/autobrief-insight.git)
cd autobrief-insight
