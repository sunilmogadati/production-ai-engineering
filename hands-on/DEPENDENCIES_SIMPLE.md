# useEffect Dependencies: Simple Explanation

## The Question
> "What exactly is dependency1, dependency2? Are these variable values?"

**Answer: They are variable NAMES, not values.**

---

## Example: Watch a Counter

```javascript
const [count, setCount] = useState(0);

useEffect(() => {
  console.log("Effect ran! count is now:", count);
}, [count]);  // ← dependency is the VARIABLE NAME 'count'
```

### What happens:

**First render:**
- count = 0
- useEffect runs → logs "count is now: 0"

**You click a button that calls setCount(1):**
- count changes from 0 to 1
- React re-renders
- useEffect sees "count changed" → runs again → logs "count is now: 1"

**You click the button again:**
- count changes from 1 to 2
- React re-renders
- useEffect sees "count changed" → runs again → logs "count is now: 2"

---

## Three Scenarios

### Scenario 1: `[count]`
```javascript
const [count, setCount] = useState(0);

useEffect(() => {
  console.log("Watching count");
}, [count]);

// Runs when:
// - Component first mounts
// - count changes (1→2, 2→3, etc)
```

### Scenario 2: `[]` (empty)
```javascript
useEffect(() => {
  console.log("Runs once");
}, []);

// Runs when:
// - Component first mounts (only!)
// - Never again, no matter what changes
```

### Scenario 3: `[count, name]`
```javascript
const [count, setCount] = useState(0);
const [name, setName] = useState("Alice");

useEffect(() => {
  console.log("Watching both count AND name");
}, [count, name]);

// Runs when:
// - Component first mounts
// - count changes (any value)
// - name changes (any value)
// - BUT NOT if something else changes (like a button press with no state update)
```

---

## Real Example: Fetch When User ID Changes

```javascript
const [userId, setUserId] = useState(1);
const [user, setUser] = useState(null);

useEffect(() => {
  // Fetch user data whenever userId changes
  console.log(`Fetching user ${userId}...`);
  fetch(`/api/user/${userId}`)
    .then(r => r.json())
    .then(data => setUser(data));
}, [userId]);  // ← Watch userId
```

**What happens:**
1. Page loads, userId = 1
2. useEffect runs → fetches user 1
3. User clicks "Next User" button
4. setUserId(2) → userId changes to 2
5. React sees userId in dependency array changed → runs useEffect
6. useEffect runs → fetches user 2
7. setUserId(3)
8. useEffect runs → fetches user 3
9. (continues...)

---

## Common Mistake: Forgetting Dependencies

```javascript
const [count, setCount] = useState(0);
const [timer, setTimer] = useState(0);

// ❌ BAD - no dependency array
useEffect(() => {
  const interval = setInterval(() => {
    setTimer(timer + 1);  // Uses old 'timer' value!
  }, 1000);
});

// Timer goes: 0, 1, 0, 1, 0, 1... (stuck!)
// Why? Every render creates a new interval, old timer value is used.
```

```javascript
// ✓ GOOD - watch timer
useEffect(() => {
  const interval = setInterval(() => {
    setTimer(t => t + 1);  // Use function form to avoid stale value
  }, 1000);
}, []);  // Run once

// Timer goes: 0, 1, 2, 3, 4... (correct!)
```

---

## When to Use useEffect

| Situation | Use useEffect? | Dependency Array |
|-----------|---|---|
| Fetch data when component mounts | Yes | `[]` |
| Fetch data when an ID changes | Yes | `[id]` |
| Display a value from props | No | — |
| Call a function on button click | No | — |
| Set up a timer | Yes | `[]` |
| Update state based on another state | No | — |

---

## TLDR

**Dependencies = variables to watch**

```javascript
useEffect(() => {
  doSomething();
}, [variablesToWatch]);

// If variablesToWatch changes → run doSomething again
// If variablesToWatch doesn't change → skip it
```

**Three patterns:**
- `[]` = run once on mount
- `[var]` = run when var changes
- `[var1, var2]` = run when either changes

---

## NOT Used in step1.html or step2.html

Both files don't fetch data or have side effects, so they don't use useEffect.

useEffect is for:
- Fetching data from an API
- Setting up timers
- Subscribing to events
- Logging

If you're just displaying props or managing local state with buttons, you don't need useEffect.
