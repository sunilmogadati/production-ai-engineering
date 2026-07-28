# Demo: watching a model learn, in VS Code

The goal isn't to *read* about gradient descent — it's to **watch the two knobs move**
in the debugger's Variables panel, one step at a time, and realise there's no magic in there.

Pairs with `study-docs/ML_Study_01` §3.4–3.7.

---

## Setup (once, ~2 min)

1. **Open the repo folder** in VS Code — `File → Open Folder…` → pick
   `production-ai-engineering` (the **repo root**, not `hands-on/`).
   *Why the root: the `.vscode/launch.json` that makes F5 work lives there.*
2. **Install the Python extension** if you don't have it (Extensions panel → search "Python" → Microsoft's).
3. **Pick your interpreter:** `Cmd/Ctrl + Shift + P` → *Python: Select Interpreter* → choose any Python 3.
   *This file needs **no** packages — no numpy, no scikit-learn. Plain Python.*
4. Open `hands-on/hello_gradient_descent.py`.

---

## Act 1 — Just run it (30 sec)

Press **`Ctrl + F5`** (Run Without Debugging), or in a terminal:

```bash
python3 hands-on/hello_gradient_descent.py
```

You get the training table, the grade against the exact formula, and the takeaways.

**Say this:** *"It started with a flat line predicting zero sales. 1,035 rounds of arithmetic
later it found `sales = 3 + 1.9 × spend` — the same answer algebra proves exactly. Nobody told
it the formula. Now let's watch it actually happen."*

---

## Act 2 — The debugger (the whole point) 🎯

This is where it lands. We freeze the loop mid-step and watch the knobs move.

### 1. Set a **conditional** breakpoint

Find this line inside `train()`:

```python
slope0, slope1 = slopes(theta0, theta1)
```

- Click the gutter to the **left of the line number** → a red dot appears.
- **Right-click the red dot → *Edit Breakpoint…* → Expression** → type:

  ```
  i <= 3
  ```

> **Do not skip the condition.** Without it the debugger stops **1,035 times** and the demo dies.
> With it, you stop only on the first 3 rounds — exactly the interesting ones.

### 2. Add Watch expressions

Open the **Run and Debug** panel (`Cmd/Ctrl + Shift + D`). In the **WATCH** section, click **+** and add:

| Add this | It shows |
|---|---|
| `theta0` | the line's starting height |
| `theta1` | the line's steepness |
| `slope0` | which way the height knob should move |
| `slope1` | which way the steepness knob should move |
| `cost(theta0, theta1)` | the badness score, live |

### 3. Press **F5** and step with **F10**

Now narrate the loop as you step:

| Step onto… | Point at the Watch panel and say |
|---|---|
| `slopes(theta0, theta1)` | *"We're standing still, feeling the ground. Both readings come from the **same spot**."* |
| after it runs | *"`slope0` is **−7.75** — **negative**. Negative means our line sits too **low**."* |
| `temp0 = ...` / `temp1 = ...` | *"We work out where each knob **should** go — but we don't move yet."* |
| `theta0, theta1 = temp0, temp1` | **The money moment.** *"Watch — **both** knobs change on this one line. Not one, then the other. Together."* |
| `current_cost = cost(...)` | *"32.4 → 11.3. One step, and the score fell by two-thirds."* |

Press **F5** again to jump to round 2, then round 3. Then **remove the breakpoint** and F5 to let it finish.

**The line that lands it:** *"That's it. That's training. A loop, two subtractions, repeat a thousand times.
Everything else in AI is this same move with more knobs."*

---

## Act 3 — Break it on purpose (live experiments)

Edit a value at the top of the file, re-run (`Ctrl + F5`), watch what changes. **This is the best part —
let students call out predictions first.**

*(All four verified — these are what actually happens, not what should happen.)*

| Change | Set it to | What actually happens | The lesson |
|---|---|---|---|
| `ALPHA = 0.05` | `0.5` | Cost goes **32 → 322 → 3,244 → 32,703 → 3.3 million**, then the panic-button exit fires: *"knobs flying off"* | Steps too big — it leaps clean over the valley and lands **higher** on the far wall, every time (§3.6). Cost **rising** is the classic "your α is too big" symptom. |
| `ALPHA = 0.05` | `0.001` | Hits the 3,000 cap, stuck at θ₁ = 2.36 (should be 1.9) | Steps too small — still crawling when the safety cap fires. **Exit condition 3, live.** |
| `THETA1_START = 0.0` | `5.0` | Converges at iter 1,107 to the same 3.0 / 1.9 — approaching from *above* | Starting point doesn't matter — one bowl, one bottom (§3.8) |
| `TOLERANCE = 1e-9` | `1e-2` | Quits at **iteration 9** with θ₀=1.02, θ₁=2.55 — badly wrong | The scary one. It **says "converged"** and hands you a confidently wrong model. "Converged" is a **choice you set**, not a fact the data tells you. |

> **Best demo of the four is the last one.** It doesn't crash and it doesn't look broken — it prints
> `STOP: cost stopped dropping (converged)` and returns garbage. Ask the room: *"It told us it converged.
> Did it?"* That's the difference between running ML and understanding it.

### The honest experiment
In `train()`, replace the simultaneous update with a sequential one:

```python
theta0 = theta0 - ALPHA * slope0     # move theta0 first...
slope0, slope1 = slopes(theta0, theta1)   # ...then re-read from the NEW spot
theta1 = theta1 - ALPHA * slope1
```

It **still lands on 3.0 / 1.9.** That's the point of the BONUS section the script already prints:
on a convex bowl both recipes arrive. Simultaneous matters because the *gradient* means
"all slopes measured at the same point" — not because you'll get a wrong number here.
Teach the honest version; students remember the teacher who didn't cry wolf.

---

## If something breaks

| Symptom | Fix |
|---|---|
| F5 does nothing / no config | You opened `hands-on/` instead of the **repo root**. Reopen the root folder. |
| Debugger stops 1,000+ times | Your breakpoint has no condition. Right-click it → *Edit Breakpoint* → `i <= 3`. |
| "Python not found" | `Cmd/Ctrl + Shift + P` → *Python: Select Interpreter*. |
| Watch shows `<error>` | You're paused outside `train()`, so `theta0` doesn't exist yet. Step until you're inside the loop. |
