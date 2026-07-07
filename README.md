# 🥦 NutriSage AI — AI-Powered Nutrition Agent

> A production-ready, full-stack nutrition assistant built with **Python Flask**, **IBM watsonx.ai**, and **IBM Granite** models. Features personalised Indian meal plans, RAG-grounded Q&A, food logging, BMI calculation, health advisory, and family profile management.

---

## 🗂️ Project Structure

```
nutrition_agent/
├── app.py                      # Flask entry point — all routes
├── config.py                   # Central configuration (env-driven)
├── requirements.txt            # Pinned Python dependencies
├── .env.example                # Environment variable template
├── README.md
│
├── agents/
│   ├── __init__.py
│   ├── instructions.py         # ✏️  EDITABLE agent persona & safety rules
│   ├── llm_client.py           # IBM watsonx.ai / Granite wrapper
│   ├── nutrition_agent.py      # RAG + LLM Q&A agent
│   ├── diet_agent.py           # 7-day personalised meal plan agent
│   ├── health_agent.py         # Preventive health advisory agent
│   └── food_log_agent.py       # Calorie estimation & daily feedback agent
│
├── rag/
│   ├── __init__.py
│   ├── pipeline.py             # CLI ingestion: load → split → embed → save
│   ├── document_loader.py      # PDF + text file loader & splitter
│   ├── embedder.py             # sentence-transformers embedding wrapper
│   ├── vector_store.py         # FAISS build / save / load
│   ├── retriever.py            # NutritionRetriever (top-k similarity search)
│   └── data/
│       ├── nutrition_reference.txt
│       └── indian_nutrition.txt
│
├── database/
│   └── models.py               # SQLAlchemy: FamilyMember, FoodLog, MealPlan
│
├── utils/
│   ├── bmi_calculator.py       # BMI + TDEE calculation
│   └── helpers.py              # Shared formatting helpers
│
├── templates/
│   ├── base.html               # Bootstrap 5 base layout, dark/light mode
│   ├── index.html              # Landing page
│   ├── chat.html               # AI Chat interface
│   ├── dashboard.html          # Nutrition dashboard
│   ├── meal_planner.html       # 7-day meal planner
│   ├── food_log.html           # Food diary & AI analysis
│   ├── bmi_calculator.html     # BMI calculator with scale
│   └── family_profiles.html    # Family member management
│
├── static/
│   ├── css/style.css           # Custom CSS (animations, dark mode, chat)
│   ├── js/app.js               # Theme toggle, nav highlight, helpers
│   └── images/
│
└── uploads/                    # User-uploaded files
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.11+
- IBM Cloud account with watsonx.ai access
- An active watsonx.ai project

### 1. Clone the repository
```bash
git clone https://github.com/your-org/nutrition_agent.git
cd nutrition_agent
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Activate
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and fill in:
```dotenv
IBM_API_KEY=<your IBM Cloud API key>
PROJECT_ID=<your watsonx.ai project ID>
IBM_URL=https://us-south.ml.cloud.ibm.com
MODEL_ID=ibm/granite-3-2-8b-instruct
SECRET_KEY=<random strong key>
```

### 5. Build the RAG knowledge index
```bash
python -m rag.pipeline
```
This loads all `.txt` and `.pdf` files from `rag/data/`, embeds them with
`sentence-transformers/all-MiniLM-L6-v2`, and saves the FAISS index to
`rag/faiss_index/`.

### 6. Run the application
```bash
python app.py
```
Visit **http://localhost:5000** in your browser.

---

## 🌐 Application Pages

| URL | Description |
|---|---|
| `/` | Landing page with feature overview |
| `/chat` | AI nutrition Q&A powered by Granite + RAG |
| `/dashboard` | Calorie & nutrient summary, daily AI feedback |
| `/meal-planner` | Generate 7-day personalised Indian meal plan |
| `/food-log` | Log meals, get AI calorie estimates, daily feedback |
| `/bmi-calculator` | BMI + TDEE calculator with health classification |
| `/family-profiles` | Add/manage family members with individual plans |

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | `{"question": "…"}` → Granite answer |
| `POST` | `/api/diet-plan` | Profile JSON → 7-day meal plan |
| `POST` | `/api/health-advice` | `{"condition":"…"}` → health tips |
| `POST` | `/api/food-log` | `{"food_name":"…","quantity":"…"}` → log + nutrition |
| `GET`  | `/api/food-log` | List recent food log entries |
| `DELETE` | `/api/food-log/<id>` | Delete a food log entry |
| `GET`  | `/api/daily-feedback` | AI feedback on today's food log |
| `POST` | `/api/bmi` | `{"weight_kg":…,"height_cm":…}` → BMI result |
| `GET`  | `/api/family` | List family members |
| `POST` | `/api/family` | Create a family member |
| `PUT`  | `/api/family/<id>` | Update a family member |
| `DELETE` | `/api/family/<id>` | Delete a family member |

---

## 🤖 Customising Agent Behaviour

All agent personas, safety rules, tone, and Indian food preferences are
defined as plain-text constants at the top of each agent file. Edit these
files to customise without touching any application logic:

| File | What to edit |
|---|---|
| [`agents/instructions.py`](agents/instructions.py) | NutriSage persona, capabilities, safety rules, Indian food context |
| [`agents/diet_agent.py`](agents/diet_agent.py) | `DIET_AGENT_INSTRUCTIONS` — meal plan format and rules |
| [`agents/health_agent.py`](agents/health_agent.py) | `HEALTH_AGENT_INSTRUCTIONS` — health advisory rules |
| [`agents/food_log_agent.py`](agents/food_log_agent.py) | `FOOD_LOG_AGENT_INSTRUCTIONS` — nutrition estimation rules |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask 3 |
| AI / LLM | IBM watsonx.ai + IBM Granite (`ibm/granite-3-2-8b-instruct`) |
| RAG | LangChain 0.2 + FAISS + sentence-transformers |
| Database | SQLite + SQLAlchemy + Flask-SQLAlchemy |
| Frontend | Bootstrap 5.3 + Bootstrap Icons + Vanilla JS |

---

## 🚀 Deployment

### Using Gunicorn (production)
```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Environment variables for production
```dotenv
DEBUG=False
SECRET_KEY=<long random string>
IBM_API_KEY=<prod key>
PROJECT_ID=<prod project>
DATABASE_URI=sqlite:///database/nutrition.db   # or PostgreSQL URI
```

### Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m rag.pipeline
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.
