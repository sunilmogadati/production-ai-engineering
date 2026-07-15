# Study Path: ML Concepts → Production → React

Follow this path to understand everything we built today.

---

## Phase 1: Understand Hyperparameters (30 min)

### Step 1: Read the theory
Open `LEARNING_GUIDE.md` **Section 1: Hyperparameters**

Key takeaways:
- Hyperparameter = setting you choose before training
- Random Forest: robust by default (barely needs tuning)
- XGBoost: powerful but needs careful tuning
- More trees ≠ better accuracy (our 300 → 100 tuning story)

### Step 2: See it in action
```bash
# Yesterday (overfit)
./venv/bin/python ml05_xgboost.py
# Output: XGBoost 79.2% vs Random Forest 81%

# Today (tuned)
# (runs again with the updated hyperparams)
# Output: XGBoost 80% vs Random Forest 81% (tied!)
```

Read the comments in `ml05_xgboost.py` to see what changed.

---

## Phase 2: Understand Decision Trees as If-Else (20 min)

### Step 1: Read the theory
Open `LEARNING_GUIDE.md` **Section 2: Decision Trees as If-Else**

Key takeaway:
- A trained tree can be converted to Python code
- The splits (thresholds) were learned from data, not guessed

### Step 2: See the actual tree
```bash
./venv/bin/python ml03_decision_tree.py
```

Look at the output — the tree structure shows:
```
|--- prior_purchases <= 2.5
|   |--- intent_signal <= 60
|   |   |--- budget <= 76: CLASS 0
```

This is literally an if-elif-elif structure. It's readable!

### Step 3: Compare to rules
Same script shows accuracy:
- Hand-written rules: 59.5%
- Learned tree: 76.2%

"Nobody wrote an if-elif for prior_purchases. The tree learned it."

---

## Phase 3: Understand Logistic Regression (20 min)

### Step 1: Run the demo
```bash
./venv/bin/python ml02_logistic_regression.py
```

### Step 2: Read the comments
The file has detailed comments explaining:
- Sigmoid function (squashes numbers into 0-1)
- Weighted sum (scorecard)
- Gradient descent (nudge weights downhill)

### Step 3: See the learned weights
The output shows:
```
intent_signal  +0.123  (positive = pushes toward convert)
budget         +0.456
prior_purchases +0.789
```

Bigger = stronger signal. Nobody wrote these; the model learned them.

---

## Phase 4: Train Time vs Serve Time (30 min)

### Step 1: Run training
```bash
./venv/bin/python ml11_train_and_save_prospect_model.py
```

Read the comments — see the 7 steps:
1. Load data
2. Split train/test
3. Train model
4. Evaluate
5. Save binary file
6. Save metadata
7. Report results

Output: two files saved
```
models/prospect_model.joblib  (binary weights)
models/prospect_model.json    (human-readable contract)
```

### Step 2: Understand the two-file pattern
Open `CONCEPTS_QUICK_REFERENCE.md` **MODEL_PATH vs META_PATH**

Why both?
- `.joblib`: The model (what scikit-learn needs to predict)
- `.json`: The contract (what humans need to understand what the model expects)

### Step 3: Run serve time (no retraining!)
```bash
./venv/bin/uvicorn serve:app --reload
curl http://127.0.0.1:8000/api/meta
```

Notice: the server loaded `.joblib` and `.json` once at startup.
Now for every request, it just predicts (never retrains).

This is the production pattern: train once, serve many times.

---

## Phase 5: React: One Component (20 min)

### Step 1: Open the file
Open `static/step1.html` in your editor

### Step 2: Understand the structure
```javascript
function ProspectCard(props) {
  return <div>{props.customer_id}</div>;
}

function App() {
  const prospects = [...];
  return prospects.map(p => <ProspectCard prospect={p} />);
}
```

A component = function that:
- Takes props (inputs)
- Returns JSX (rendered HTML)

### Step 3: See it in a browser
```bash
./venv/bin/python -m http.server 8001 --directory static
```
Open http://127.0.0.1:8001/step1.html

Three cards, each rendered by ProspectCard component.
No state, no API, no side effects — pure display.

### Step 4: Read the comments
Every function has comments explaining:
- What is a component
- What are props
- Why we use `.map()` to render lists

---

## Phase 6: React: State + Callbacks (30 min)

### Step 1: Understand useState
Open `LEARNING_GUIDE.md` **Section 5: React Hooks → useState**

Key:
```javascript
const [count, setCount] = useState(0);
setCount(count + 1);  // Updates state, triggers re-render
```

### Step 2: Understand the parent-child pattern
Open `CONCEPTS_QUICK_REFERENCE.md` **Props Down, Callbacks Up**

Key:
```javascript
// Parent
<ScoreForm onScore={handleScore} />

// Child
<button onClick={() => props.onScore(formData)}>Score</button>

// Parent's handleScore
const handleScore = async (formData) => {
  const result = await fetch("/api/score", ...);
  setProspects([result, ...prospects]);
};
```

The child doesn't fetch; the parent does.
The child just calls a callback.

### Step 3: See it in a browser
Make sure both servers are running:
```bash
# Terminal 1: API
./venv/bin/uvicorn serve:app --reload

# Terminal 2: Static files
./venv/bin/python -m http.server 8001 --directory static
```

Open http://127.0.0.1:8001/step2.html

- Fill in the form, click "Score"
- The parent fetches from /api/score
- The list updates
- Try multiple times to see it accumulate

### Step 4: Trace through the code
Read `static/step2.html` with the comments:
- ProspectList: presentation only
- ScoreForm: has state, calls callback
- App: parent state, fetches API, passes results

---

## Phase 7: The Full App (10 min)

### Step 1: See the final result
Open http://127.0.0.1:8000

- Model card at the top (version, accuracy, thresholds)
- Three columns (🔥 Hot / 🌤 Warm / 🧊 Cold)
- What-if scorer
- Prospects sorted hottest-first
- Limit selector
- Error handling

### Step 2: Spot the teaching moment
Look at the top hot prospects:
- CUST-1002: intent 69 → hot (94%)
- CUST-1003: intent 71 → hot (88%)

Then look at cold prospects:
- CUST-1001: intent 81 → cold (15%)

"Why is a lead with intent 81 rated COLD while a lead with intent 69 is rated HOT?"

Answer: The model learned interactions. Intent 81 might have low budget, no prior purchases, or wrong ad channel. The forest considered all factors together, not just intent.

This is why hand-written rules fail. A rule `if intent > 75: convert` would get this wrong.

---

## Quick Verification Checklist

Before presenting to the class, verify:

- [ ] `ml05_xgboost.py` shows XGBoost ~80% (tuned)
- [ ] `ml03_decision_tree.py` shows tree structure (if-elif-else)
- [ ] `ml11_train_and_save_prospect_model.py` produces model files
- [ ] `serve.py` is running on http://127.0.0.1:8000
- [ ] `step1.html` shows three hardcoded prospect cards
- [ ] `step2.html` responds to the form (hit /api/score)
- [ ] `index.html` shows full dashboard with model card

---

## Teaching Angles by Concept

### Hyperparameters
"Tuning isn't magic. More trees = worse on this small dataset. Why? Overfitting."

### Decision Trees
"This is literally if-elif code. Nobody wrote it. The machine learned it from data."

### Sigmoid & Gradient Descent
"Logistic regression learns a weighted scorecard. Each weight pushes the score up or down. Gradient descent finds the best weights."

### Train vs Serve
"Training is expensive (needs data, careful tuning, takes time). Serving is cheap (load file, predict, return JSON). That's why we train once."

### Feature Contract
"If the serving code builds features in the wrong order, predictions are garbage. That's why we save the feature list in JSON."

### React Components
"Components = functions. Props = inputs. State = changeable data. Callbacks = how children talk to parents."

---

## Time Estimate for Full Walkthrough

- Phase 1 (Hyperparameters): 30 min
- Phase 2 (Decision Trees): 20 min
- Phase 3 (Logistic Regression): 20 min
- Phase 4 (Train vs Serve): 30 min
- Phase 5 (React Components): 20 min
- Phase 6 (React State): 30 min
- Phase 7 (Full App): 10 min
- Q&A: 20 min

**Total: ~3 hours** (break into 2 sessions if needed)

---

## Files to Have Open During Presentation

1. `ml03_decision_tree.py` (tree structure)
2. `ml05_xgboost.py` (tuning story)
3. `LEARNING_GUIDE.md` (concepts)
4. `static/step1.html` (component basics)
5. `static/step2.html` (state + callbacks)
6. Browser with http://127.0.0.1:8000 (final app)
7. Browser with /docs (Swagger API)
