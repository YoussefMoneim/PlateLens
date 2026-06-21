# 🍽 PlateLens — AI Nutrition Assistant

An agentic AI system that analyzes food images to suggest recipes and provide detailed nutritional breakdowns.

Built with **CrewAI**, **IBM WatsonX**, **Pydantic**, and **Gradio**.

> 🔎 **Try the interactive demo** — no setup, no API key needed. A static showcase of the full agent pipeline with real captured outputs lives in [`/demo`](./demo). Open `demo/index.html` in any browser, or deploy it free on GitHub Pages.

---

## What it does

Upload a photo of your fridge or a dish and PlateLens will:

**Recipe Mode** — identify ingredients → filter by dietary restrictions → suggest 3 creative recipes with calorie estimates

**Analysis Mode** — analyze the dish → break down macronutrients, vitamins, minerals → provide a health evaluation

---

## Architecture

```
Recipe Workflow:
image → [Ingredient Detection Agent] → [Dietary Filtering Agent] → [Recipe Suggestion Agent]

Analysis Workflow:
image → [Nutrient Analysis Agent]
```

Each agent is a specialist:
- **Ingredient Detection Agent** — uses a vision LLM to extract and clean ingredients
- **Dietary Filtering Agent** — filters ingredients based on vegan/keto/gluten-free etc.
- **Nutrient Analysis Agent** — provides full macronutrient + vitamin + mineral breakdown
- **Recipe Suggestion Agent** — creates 3 practical recipes with step-by-step instructions

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Orchestration | CrewAI |
| LLM (Vision) | meta-llama/llama-3-2-90b-vision-instruct via IBM WatsonX |
| LLM (Text) | ibm/granite-4-h-small via IBM WatsonX |
| Structured Outputs | Pydantic v2 |
| Agent Config | YAML |
| UI | Gradio |

---

## Project Structure

```
platelens/
├── app.py                  ← Gradio UI + main entry point
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── crew.py             ← CrewAI crew definitions
│   ├── tools.py            ← Custom LangChain tools
│   ├── models.py           ← Pydantic output schemas
│   └── config/
│       ├── agents.yaml     ← Agent roles, goals, backstories
│       └── tasks.yaml      ← Task descriptions and expected outputs
└── examples/               ← Sample food images
```

---

## Setup

```bash
git clone https://github.com/YoussefMoneim/PlateLens.git
cd PlateLens
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

---

## Key Concepts Demonstrated

- **Multi-agent orchestration** with CrewAI's sequential process
- **YAML-based agent configuration** — roles and tasks defined declaratively
- **Task-level context passing** — dietary filtering reads ingredient detection output
- **Pydantic structured outputs** — guaranteed JSON schema for recipes and analysis
- **Vision LLM integration** — base64 image encoding for multimodal models
- **Separation of concerns** — tools, agents, tasks, and UI are all independent modules
