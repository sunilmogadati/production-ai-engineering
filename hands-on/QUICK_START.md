# Quick Start (5 Minutes)

**TL;DR version of FULL_SETUP_GUIDE.md**

## 1. Get API Key
Go to https://console.anthropic.com → API Keys → Create Key → Copy it

## 2. Terminal Setup

```bash
cd /Users/sunilmogadati/Downloads/fastapi-hello
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR .\venv\Scripts\Activate.ps1  # Windows
```

## 3. Install Everything

```bash
pip install anthropic fastapi uvicorn pandas scikit-learn joblib python-dotenv
```

## 4. Set API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
# Replace with your actual key from step 1
```

## 5. Train Model

```bash
python ml11_train_and_save_prospect_model.py
```

## 6. Run Server

```bash
uvicorn serve:app --reload
```

Open browser: **http://127.0.0.1:8000**

---

## That's It! Now Try:

**Prompt scripts** (open a new terminal, keep server running):
```bash
source venv/bin/activate
python prompt01_hello_world.py
python prompt02_conversation.py
python prompt03_system_prompt.py
python prompt04_structured_output.py
python prompt05_temperature.py
```

**Dashboard features:**
- See prospects ranked by conversion probability
- Click any prospect → see phone, call history, suggested script
- Use the "What-if" form to score your own prospect

---

## Stuck?

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Run `pip install anthropic fastapi` etc. |
| 401 Unauthorized | Check `echo $ANTHROPIC_API_KEY` is not empty |
| Port 8000 in use | Run `uvicorn serve:app --reload --port 8001` |
| Model not found | Run `python ml11_train_and_save_prospect_model.py` |

---

See **FULL_SETUP_GUIDE.md** for complete details.
