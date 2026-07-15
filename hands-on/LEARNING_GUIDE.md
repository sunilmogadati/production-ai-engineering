# Learning Guide: ML Concepts & Code Annotations

## 1. Hyperparameters: XGBoost vs Random Forest vs Logistic Regression

### What is a Hyperparameter?
A **hyperparameter** is a setting you choose *before* training. The model learns its **parameters** (weights, tree splits) *during* training. You set hyperparameters, the model finds parameters.

**Analogy**: Hyperparameters = recipe instructions you give. Parameters = the actual cake.

---

### Random Forest Hyperparameters
Random Forest has very few important hyperparams — it's designed to be robust with defaults:

```python
RandomForestClassifier(
    n_estimators=300,      # How many trees? (more = usually better, but slower)
    random_state=42,       # Seed for reproducibility
    max_depth=None,        # Tree depth limit (None = grow until pure)
    min_samples_split=2,   # Min samples to split a node (prevents overfitting)
)
```

**The key insight**: Random Forest doesn't need much tuning. Bagging (averaging many trees) is naturally robust. More trees almost always helps. It's the "robust default" — why we tested it.

---

### XGBoost Hyperparameters (where tuning matters)
XGBoost is more powerful but requires tuning — it can easily overfit:

```python
XGBClassifier(
    n_estimators=100,           # Boosting rounds (NOT independent trees)
    max_depth=3,                # Tree depth (shallow = less overfit, deep = more flexible)
    learning_rate=0.05,         # Step size (how much each tree corrects the last)
                                # Lower = slower learning, less overfit
    subsample=0.8,              # Use 80% of rows per tree (like bagging)
    colsample_bytree=0.8,       # Use 80% of features per tree
    reg_alpha=0,                # L1 penalty (Lasso: reduce # of features)
    reg_lambda=1,               # L2 penalty (Ridge: shrink weights)
)
```

**Why the gap in performance?**
- We trained your XGBoost with `n_estimators=300` (too many boosting rounds for 1600 training rows)
- It fit noise in the training data
- We dialed it back: 100 trees, depth 3, learning_rate 0.05
- Suddenly it's competitive again

**Analogy**: Random Forest = "I'll vote on a bunch of independent opinions." XGBoost = "I'll teach each tree what the previous trees got wrong." The second is powerful but risky if you let it learn for too long.

---

### Logistic Regression: Sigmoid + Loss Function + Gradient Descent

#### The Pipeline
```
Raw output (z) → Sigmoid (squash to 0-1) → Probability → Compare to truth → Loss → Gradient → Update weights
```

#### Sigmoid Function
```python
sigmoid(z) = 1 / (1 + e^(-z))
```
- Takes any number (negative ∞ to +∞)
- Outputs a probability (0 to 1)
- Steep in the middle (sensitive), flat at edges (insensitive)

#### Loss Function (NOT Mean Squared Error)
Logistic regression uses **Binary Cross-Entropy Loss**, NOT MSE:

```python
loss = -[y * log(pred) + (1-y) * log(1-pred)]
```

**Why not MSE?** MSE is smooth everywhere; cross-entropy has steep gradients near the right answer, which helps the optimizer correct confidently wrong predictions.

#### How It Corrects Weights: Gradient Descent
1. Compute loss for all training samples
2. Calculate the **gradient** (slope) of loss w.r.t. each weight
3. Move each weight slightly *down* the gradient (like sliding down a hill)
4. Repeat 100s of times

This is **similar** to backpropagation in deep learning:
- **Logistic regression**: calculus + chain rule on one operation (sigmoid)
- **Deep learning**: calculus + chain rule on *many* operations (many layers)
- The idea is identical; the complexity is different

---

## 2. Decision Trees as If-Else Statements

A trained tree can literally be converted to if-else code. Here's how:

### Example: A tiny trained tree
```
        intent > 50?
       /          \
     YES            NO
     /                \
budget > 100?       convert=0
/         \
YES        NO
/            \
convert=1   convert=0
```

### As Python code:
```python
def tree_predict(intent, budget):
    if intent > 50:
        if budget > 100:
            return 1  # high probability of conversion
        else:
            return 0
    else:
        return 0  # low intent = no conversion

# This is literally what your trained tree is doing!
```

### To see your actual tree:
```python
from sklearn import tree

# After training:
tree.plot_tree(model, feature_names=FEATURES, class_names=["no", "yes"])
# This draws the actual if-else structure your model learned
```

Random Forest is 300 of these trees voting. XGBoost is 100 trees where each learns from the last tree's mistakes.

---

## 3. MODEL_PATH vs META_PATH: The Two-File Pattern

### MODEL_PATH: The Weights
```python
MODEL_PATH = Path("models/prospect_model.joblib")
```
- Binary file containing the trained model's internal state
- For a tree: all the split points and leaf values
- For Random Forest: 300 trees worth of data
- **Can only be loaded by the exact same library** (scikit-learn)
- ~1-10 MB typically

### META_PATH: The Contract
```python
META_PATH = Path("models/prospect_model.json")
```
- Human-readable JSON with metadata:
```json
{
  "model_version": "1.0",
  "model_type": "RandomForestClassifier",
  "test_accuracy": 0.81,
  "features": ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"],
  "training_rows": 1600
}
```

### Why Both?
- **joblib** = the model (load it, predict)
- **JSON** = the contract (what features does it expect? in what order? how accurate was it?)
- At serving time (ml10, serve.py), you must:
  1. Load the model from joblib
  2. Read the JSON to see what features it expects
  3. Build features in **exactly that order** or predictions are garbage

This separation is **critical** in production: the JSON documents the feature contract so different teams (data scientist, engineer) can stay in sync.

---

## 4. React in Static HTML (No Build Step)

### Yes! We're doing it.
```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```

We download React from a **CDN** (Content Delivery Network). No `npm install`, no webpack, no build step.

### Vite / Next.js
These are **build tools** for when you have:
- Many source files
- Complex dependencies
- Want optimizations
- Build-time type checking (TypeScript)

For a class demo? Static HTML + CDN React is simpler and faster.

---

## 5. React Hooks Explained (in our code)

### `useState`
```javascript
const [count, setCount] = useState(0);
```
- **State** = data that can change
- When state changes, React re-renders
- `count` = current value
- `setCount` = function to update it
- `0` = initial value

### `useEffect`
```javascript
useEffect(() => {
  console.log("Component mounted or dependencies changed");
}, [dependency1, dependency2]);
```
- Runs code **after** render (not during)
- If dependency array is empty `[]`, runs once on mount
- If dependencies listed, runs whenever they change
- Used for: fetching data, setting up listeners, timers

**Without useEffect**: your component renders, and the API call happens during render (bad — can cause infinite loops).

**With useEffect**: render happens first, then your code runs.

---

## 6. Logistic Regression: Sigmoid + Weights

During training:
1. Start with random weights
2. For each batch of data:
   - Compute: `z = w1*x1 + w2*x2 + ... + b`
   - Apply sigmoid: `pred = 1 / (1 + e^(-z))`
   - Compute loss: `-[y*log(pred) + (1-y)*log(1-pred)]`
   - Compute gradient: how much does each weight affect the loss?
   - Update: `w = w - learning_rate * gradient`

This continues for 100-1000 iterations (epochs) until the loss stops decreasing.

It's **not** backpropagation (that's deep learning). It's just gradient descent on a single sigmoid. But the *idea* is identical.

---

## 7. Summary: The Model Ladder

```
Hand-written rules    -> Logistic Regression -> Decision Tree -> Random Forest -> XGBoost
(Explainable, brittle)  (Linear boundary)      (Axis-aligned)   (Robust, black-box) (Powerful, needs tuning)
accuracy ~60%           accuracy ~72%           accuracy ~78%    accuracy ~81%     accuracy ~80% (without tuning)
```

Each step:
- Trades explainability for accuracy (harder to explain the model's decision)
- Adds complexity (more hyperparams to tune)
- Becomes more robust to different data

Your job: pick the right one for the business need, not the leaderboard.
