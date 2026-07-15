# Quick Reference: ML & React Concepts

## ML Concepts

### Hyperparameters
**What**: Settings you choose *before* training.  
**Example**: `n_estimators=300, max_depth=4, learning_rate=0.05`  
**When to tune**: XGBoost needs tuning; Random Forest doesn't.

### Sigmoid Function
**What**: Squashes any number (-∞ to +∞) into probability (0 to 1).  
**Formula**: `sigmoid(z) = 1 / (1 + e^(-z))`  
**Used in**: Logistic regression (converts scores to probabilities).

### Cross-Entropy Loss
**What**: Measures how wrong a probability prediction is (for classification).  
**Used by**: Logistic regression, neural networks.  
**NOT Mean Squared Error**: MSE is for regression (predicting numbers), not classification.

### Gradient Descent
**What**: Optimization algorithm. Nudge weights downhill (toward lower loss).  
**Steps**:
  1. Compute loss (how wrong are we?)
  2. Compute gradient (which way downhill?)
  3. Move weights down: `w = w - learning_rate * gradient`
  4. Repeat

**Similar in Deep Learning**: Same idea, but backpropagation applies chain rule through many layers.

### Decision Tree as If-Else
**How it works**: Splits on one feature at a time (learned thresholds, not hand-written).  
**Can be converted to code**:
```python
def predict(intent, budget):
    if intent > 68:
        if budget > 114:
            return 1  # convert
        else:
            return 0
    else:
        return 0
```

### MODEL_PATH vs META_PATH
| File | Format | Contains | Used for |
|------|--------|----------|----------|
| model.joblib | Binary | Trained weights, tree structure | predict_proba() calls |
| model.json | Text | Feature names, order, accuracy, version | Knowing the contract |

**Why both?** Separation of concerns. The binary is what the model needs; the JSON is what humans and APIs need.

---

## React Concepts

### Component
**What**: A JavaScript function that returns JSX (looks like HTML).  
**Props**: The inputs to a component (like function arguments).  
**Returns**: JSX (rendered HTML).

```javascript
function ProspectCard(props) {
  return <div>{props.customer_id}</div>;
}
```

### State
**What**: Data that can change. When state changes, React re-renders.  
**Hook**: `useState`  
**Usage**: `const [value, setValue] = useState(initialValue)`

```javascript
const [count, setCount] = useState(0);
setCount(count + 1);  // Updates state, triggers re-render
```

### Hooks
**What**: Functions that let you use state and other React features.

#### useState
Adds state to a functional component.
```javascript
const [prospects, setProspects] = useState([]);
```

#### useEffect
Runs code after render (not during). Use for API calls, subscriptions, timers.
```javascript
useEffect(() => {
  fetchProspects();  // Called after render
}, []);  // Empty dependency = run once on mount
```

### Props Down, Callbacks Up
**Pattern**: 
- Parent passes data → child via **props** (props down)
- Child triggers action → parent via **callbacks** (callbacks up)

```javascript
// Parent
<ScoreForm onScore={handleScore} />

// Child
<button onClick={() => props.onScore(formData)}>Score</button>
```

When the child button is clicked, it calls the parent's `handleScore`, which can fetch from the API.

### JSX
**What**: Looks like HTML but is JavaScript.  
**Compiled to**: `React.createElement()` calls.  
**Rules**:
- One root element per component
- Use `className` not `class`
- Embed JS with `{}`

```javascript
<div className="box">
  <strong>{prospect.customer_id}</strong>
</div>
```

---

## The Flow: Train → Save → Serve → UI

### Train Time (ml11_train_and_save_prospect_model.py)
```
1. Load historical data (leads.csv)
2. Train model on subset (80%)
3. Evaluate on held-out (20%)
4. Save model.joblib + model.json
```

### Serve Time (serve.py)
```
1. Load model.joblib + model.json (once at startup)
2. For each HTTP request:
   a. Convert Lead to features (using feature contract from JSON)
   b. Call model.predict_proba
   c. Bucket into hot/warm/cold
   d. Return JSON
```

### UI Time (static/step1.html, step2.html, index.html)
```
1. Display prospects (from API or hardcoded)
2. Collect user input (what-if form)
3. Submit to /api/score
4. Display result
5. Fetch updated prospect list
6. Re-render with new data
```

---

## Files and Their Purpose

| File | Type | Purpose |
|------|------|---------|
| ml02_logistic_regression.py | ML | Weighted sum + sigmoid = probability |
| ml03_decision_tree.py | ML | If-else questions (learned, not hand-written) |
| ml04_random_forest.py | ML | 300 trees vote = robust default |
| ml05_xgboost.py | ML | 100 trees, each learns from last = powerful, needs tuning |
| ml11_train_and_save_prospect_model.py | ML | Train & save the Random Forest model |
| serve_step1.py | API | Minimal API, just /api/score endpoint |
| serve.py | API | Full API with all endpoints |
| static/step1.html | React | One component, hardcoded data (learning) |
| static/step2.html | React | Two components + state + API calls (learning) |
| static/index.html | React | Final polished dashboard |
| LEARNING_GUIDE.md | Doc | Deep explanations |
| CONCEPTS_QUICK_REFERENCE.md | Doc | This file |
| SESSION_5_PROGRESSION.md | Doc | How to run each step |

---

## The Decision Tree: If-Else Example

### Trained tree (from ml03):
```
        intent_signal <= 68?
       /                    \
     YES (convert=0)        NO
                           /
              budget <= 114?
              /            \
           YES              NO
       convert=0         convert=1
```

### As Python code:
```python
def tree_predict(intent_signal, budget):
    if intent_signal <= 68:
        return 0  # low intent = skip
    elif budget <= 114:
        return 0  # low budget = skip
    else:
        return 1  # high intent AND high budget = convert
```

This is exactly what the tree is doing internally!

---

## React in Static HTML: Why It Works

### No build step
We load React from a **CDN** (Content Delivery Network):
```html
<script src="https://unpkg.com/react@18/..."></script>
```

### Babel compilation
Babel translates JSX → JavaScript in the browser:
```html
<script type="text/babel">
  // This JSX is compiled to React.createElement calls
  function App() { return <div>Hello</div>; }
</script>
```

### When to use Vite / Next.js
- Many files (need bundling)
- Complex dependencies
- Want build-time optimizations
- TypeScript (compile-time checking)

**For classroom?** Static HTML + CDN React is simpler.

---

## Command Cheatsheet

```bash
# Train and save
./venv/bin/python ml11_train_and_save_prospect_model.py

# Serve (all endpoints)
./venv/bin/uvicorn serve:app --reload
# Open http://127.0.0.1:8000

# Serve minimal API (for learning)
./venv/bin/uvicorn serve_step1:app --reload
# Open http://127.0.0.1:8000/docs for Swagger

# Serve static files (for learning React)
./venv/bin/python -m http.server 8001 --directory static
# Open http://127.0.0.1:8001/step1.html
```
