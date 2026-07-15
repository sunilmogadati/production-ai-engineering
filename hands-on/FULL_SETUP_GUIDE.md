# Full Setup Guide: From Zero to Running Everything

Complete step-by-step instructions to get the ML cohort + Prompt Engineering cohort + interactive dashboard running.

## Prerequisites

- Python 3.9+ installed (`python --version`)
- A terminal/command line
- ~5 minutes of setup time
- An Anthropic API key (free tier is fine)

---

## Part 1: Get Your API Keys (5 min)

### Anthropic API Key

1. Go to https://console.anthropic.com
2. Sign up or log in with your email
3. Click **"API Keys"** in the left sidebar
4. Click **"Create Key"**
5. Copy the full key (starts with `sk-ant-`)
6. **Save it.** You'll only see it once.

---

## Part 2: Clone/Enter the Repository (2 min)

```bash
# Navigate to the project
cd /Users/sunilmogadati/Downloads/fastapi-hello

# Check you're in the right place
pwd
# Should show: /Users/sunilmogadati/Downloads/fastapi-hello

# List files to confirm
ls -la
# Should see: main.py, serve.py, requirements.txt, etc.
```

---

## Part 3: Create a Virtual Environment (2 min)

A virtual environment keeps Python packages isolated for this project.

### macOS / Linux

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt now
```

### Windows (PowerShell)

```powershell
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt now
```

---

## Part 4: Install Python Dependencies (2 min)

Make sure you have the virtual environment activated (see step 3).

### Install the ML + FastAPI dependencies

```bash
# Install everything listed in requirements.txt
pip install --upgrade pip setuptools wheel

pip install anthropic fastapi uvicorn pandas scikit-learn joblib python-dotenv
```

**What this installs:**
- `anthropic` - Anthropic API SDK (prompt engineering)
- `fastapi` - Web framework (API server)
- `uvicorn` - ASGI server (runs FastAPI)
- `pandas` - Data manipulation (ML)
- `scikit-learn` - ML models (logistic regression, decision trees, random forest)
- `joblib` - Save/load models
- `python-dotenv` - Load environment variables from `.env` file

**Verify installation:**

```bash
python -c "from anthropic import Anthropic; print('✓ anthropic installed')"
python -c "from fastapi import FastAPI; print('✓ fastapi installed')"
python -c "from sklearn.ensemble import RandomForestClassifier; print('✓ scikit-learn installed')"
```

All three should print checkmarks. If any fail, run the pip install again.

---

## Part 5: Set Up Your API Key (2 min)

### Option A: Create a `.env` file (Recommended)

```bash
# Create a .env file in the project root
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
EOF

# Replace YOUR-KEY-HERE with your actual key from Part 1
# Edit the file manually if needed:
nano .env
# Paste your key, then Ctrl+X, Y, Enter to save
```

### Option B: Set environment variable in terminal

**macOS / Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
# Replace sk-ant-YOUR-KEY-HERE with your actual key
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
# Replace sk-ant-YOUR-KEY-HERE with your actual key
```

**Verify it's set:**
```bash
echo $ANTHROPIC_API_KEY  # Should print your key
```

---

## Part 6: Train the ML Model (2 min)

The model needs to be trained before we can serve it.

```bash
# Make sure you're in the project directory
cd /Users/sunilmogadati/Downloads/fastapi-hello

# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Train the model
python ml11_train_and_save_prospect_model.py
```

**Expected output:**
```
Training Random Forest...
Test accuracy: 81.2%
Saved: models/prospect_model.joblib
Saved: models/prospect_model.json
✓ Model trained and ready to serve
```

If you see errors about missing data/leads.csv, the data files are already there. If it says "Test accuracy: XX%", you're good!

---

## Part 7: Verify Everything Works (1 min)

### Test 1: Run a Prompt Engineering Script

```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux

# Run hello world
python prompt01_hello_world.py
```

**Expected output:**
```
Claude says:
I'm Claude, an AI assistant made by Anthropic. I'm here to help you with a wide 
variety of tasks including writing, analysis, coding, math, creative projects, 
and general question-answering.
```

If you see Claude's response, the API key is working! ✅

### Test 2: Start the FastAPI Server

```bash
# Keep venv activated, open a NEW terminal window, navigate to the project, activate venv again

# Terminal 1: Run the FastAPI server
uvicorn serve:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Don't close this terminal. The server is running.

### Test 3: Open the Dashboard

Open your browser and go to:
```
http://127.0.0.1:8000
```

You should see:
- "Prospect Scoring Board" header
- Three columns: Hot 🔥 | Warm 🌤 | Cold 🧊
- A "What-if scorer" form
- Model info card (81.2% accuracy, etc.)

**Click on any prospect card** → see phone number, call history, suggested script!

---

## Part 8: Run the Prompt Engineering Scripts (Optional, 15 min)

With the server running in Terminal 1, open a NEW terminal and run:

```bash
# Terminal 2: Navigate and activate venv
cd /Users/sunilmogadati/Downloads/fastapi-hello
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Run each script in sequence
python prompt01_hello_world.py     # ~2 min
python prompt02_conversation.py    # ~5 min
python prompt03_system_prompt.py   # Run 3 times, notice the persona changes
python prompt04_structured_output.py  # ~5 min
python prompt05_temperature.py     # ~5 min
```

Each script should run without errors and show output in your terminal.

---

## Part 9: Run the Progressive React + ML Steps (Optional, 20 min)

With the server from Part 7 running, you can also test the progressive React steps.

### Terminal 3: Run a Static File Server

```bash
# Terminal 3: Navigate and activate venv
cd /Users/sunilmogadati/Downloads/fastapi-hello
source venv/bin/activate

# Start a simple HTTP server for static HTML
python -m http.server 8001 --directory static
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8001 (http://127.0.0.0:8001/) ...
```

Now you can visit:
- `http://127.0.0.1:8000` - Full integrated app (React + ML + FastAPI)
- `http://127.0.0.1:8001/step1.html` - Step 1: One React component
- `http://127.0.0.1:8001/step2.html` - Step 2: Two components + state
- `http://127.0.0.1:8001/step6.html` - Step 6: LLM transcript analysis

---

## Summary: All Running

When everything is working, you should have:

| Terminal | Command | URL |
|----------|---------|-----|
| 1 | `uvicorn serve:app --reload` | http://127.0.0.1:8000 |
| 2 | `python prompt01_hello_world.py` | (output in terminal) |
| 3 | `python -m http.server 8001 --directory static` | http://127.0.0.1:8001 |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
# Make sure venv is activated (see (venv) in prompt)
source venv/bin/activate  # macOS/Linux

# Reinstall
pip install anthropic
```

### "401 Unauthorized" when running prompt scripts
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
```

### "Connection refused" when opening http://127.0.0.1:8000
```bash
# Make sure you ran:
uvicorn serve:app --reload

# And didn't close that terminal
```

### "Port 8000 already in use"
```bash
# Use a different port
uvicorn serve:app --reload --port 8001

# Then open http://127.0.0.1:8001
```

### Model file not found: "models/prospect_model.joblib"
```bash
# You skipped Part 6. Train the model:
python ml11_train_and_save_prospect_model.py
```

### Click on a prospect but modal doesn't show
```bash
# Make sure you're using a modern browser (Chrome, Safari, Firefox)
# Open browser console (F12 or right-click → Inspect) and check for errors
# Try refreshing the page
```

---

## Quick Reference: All Commands

```bash
# Setup (one time)
cd /Users/sunilmogadati/Downloads/fastapi-hello
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install anthropic fastapi uvicorn pandas scikit-learn joblib python-dotenv
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY"
python ml11_train_and_save_prospect_model.py

# Running (every time you want to use it)
cd /Users/sunilmogadati/Downloads/fastapi-hello
source venv/bin/activate  # macOS/Linux

# Terminal 1: Start the server
uvicorn serve:app --reload
# Open http://127.0.0.1:8000 in your browser

# Terminal 2: Run prompt scripts
python prompt01_hello_world.py
python prompt02_conversation.py
python prompt03_system_prompt.py
python prompt04_structured_output.py
python prompt05_temperature.py

# Terminal 3: Static file server (optional)
python -m http.server 8001 --directory static
# Open http://127.0.0.1:8001/index.html
```

---

## What You Now Have

✅ **ML Cohort:**
- 11 progressive ML scripts (linear → logistic → decision trees → random forest → XGBoost)
- Saved model (prospect_model.joblib)
- FastAPI server serving the model

✅ **Prompt Engineering Cohort:**
- 5 progressive prompt scripts (hello world → conversation → system prompts → JSON extraction → temperature)
- All with extensive comments

✅ **Integration:**
- FastAPI dashboard with hot/warm/cold prospects
- Click any prospect → see phone number, call history, suggested script
- All running locally

✅ **Teaching Materials:**
- PROMPT_PROGRESSION.md - Full roadmap
- PROMPT_SETUP.md - Setup for students
- PROMPT_TEACHING_GUIDE.md - Complete lesson plan

---

## Next Steps for Your Cohort

1. **Share PROMPT_SETUP.md** with students (just API key + pip install)
2. **Run prompt01_hello_world.py** together in your first session (5 min)
3. **Go through prompt02-05** (one per day, 5-10 min each)
4. **Live-code the integration** (building a FastAPI endpoint that uses Claude)
5. **Have students build their own app** (using the patterns they learned)

---

## Getting Help

- **Anthropic Docs:** https://docs.anthropic.com
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **scikit-learn Docs:** https://scikit-learn.org
- **Anthropic Discord:** https://discord.gg/anthropic

---

**You're all set! Start with Part 7 Test 1 and work your way through. Happy teaching!**
