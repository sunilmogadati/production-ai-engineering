# React Hello World: Step 1 & Step 2

## Step 1: One Component with Props (No State)

**File**: `static/step1.html`

**What it does**:
```
Greeting("Alice") → <h2>Hello, Alice!</h2>
Greeting("Bob")   → <h2>Hello, Bob!</h2>
Greeting("Charlie") → <h2>Hello, Charlie!</h2>
```

**Concepts**:
- Component = function
- Props = inputs to the function
- JSX = HTML-like syntax

**Code**:
```javascript
function Greeting(props) {
  return <h2>Hello, {props.name}!</h2>;
}

<Greeting name="Alice" />
```

**That's it. No state, no API, no side effects.**

---

## Step 2: Parent State → Child Props → Callback

**File**: `static/step2.html`

**What it does**:
1. App (parent) has state: count = 0
2. App passes count to Display child via props
3. App passes handleClick callback to Button child via props
4. You click button → handleClick runs → setCount(count + 1)
5. App re-renders with new count
6. Display sees new props, displays new message

**Flow diagram**:
```
App (parent)
├── state: count = 0
├── passes → Display (child) { message prop }
└── passes → Button (child) { onButtonClick callback }

User clicks button
↓
Button calls props.onButtonClick()
↓
App's handleClick() runs
↓
setCount(count + 1) updates state
↓
App re-renders
↓
Display gets new props, shows new message
```

**Concepts**:
- State = data that changes
- Props down = parent sends data to child
- Callbacks up = child tells parent to do something
- Re-render = React draws again with new data

**Code**:
```javascript
function App() {
  const [count, setCount] = useState(0);

  const handleClick = () => {
    setCount(count + 1);
  };

  return (
    <>
      <Display message={`Count is ${count}`} />
      <Button onButtonClick={handleClick} />
    </>
  );
}
```

**That's the whole React story in 3 functions.**

---

## How to Try It

### Step 1: One Component
```bash
./venv/bin/python -m http.server 8001 --directory static
```
Open http://127.0.0.1:8001/step1.html

You see:
```
Hello, Alice!
Hello, Bob!
Hello, Charlie!
```

Read the code (3 lines):
- Greeting function takes props
- Returns JSX with props.name
- App calls Greeting 3 times

### Step 2: Two Components + State
Open http://127.0.0.1:8001/step2.html

You see:
- "Display Component" showing "Count is 0"
- "Button Component" with a clickable button

Click the button → count increases → Display updates

Read the code (40 lines):
- Display: receives props, displays them
- Button: receives callback, calls it when clicked
- App: has state, passes to both children

---

## The Minimal React Concept

```javascript
// 1. Component (function)
function Greeting(props) {
  return <h2>Hello, {props.name}</h2>;
}

// 2. Props (inputs)
<Greeting name="Alice" />

// 3. State (changeable data)
const [count, setCount] = useState(0);

// 4. Callbacks (child → parent communication)
<Button onClick={() => doSomething()} />
```

That's 90% of React. Everything else is build on these 4 ideas.

---

## Dependencies in useEffect (Not Used Here)

**step1 and step2 DON'T use useEffect** because they don't fetch data or have side effects.

When you DO use it:
```javascript
useEffect(() => {
  fetchData();  // Runs after render
}, [id]);       // When 'id' changes
```

- `[id]` = "watch this variable"
- If id changes: run the function
- If id doesn't change: skip it
- Empty `[]` = run once on mount

But you don't need it for basic components!

---

## Why These Are Minimal

| Thing | Step 1 | Step 2 |
|------|--------|--------|
| Lines of code | ~15 | ~50 |
| Concepts | Props only | State + Props + Callbacks |
| Data flow | One direction (down) | Both directions |
| API calls | No | No |
| Hooks | No | useState |
| Side effects | No | No |

Both are "hello world" level. Full React apps would add:
- useEffect (API calls, timers)
- More state (forms, filtering)
- Error handling
- Loading states
- etc.

But these two files show the core idea.

---

## Next Steps

1. **Modify step1.html** → Add more names, change greeting text
2. **Modify step2.html** → Change what the counter does, add more buttons
3. **Combine them** → Use step2 logic (state + callbacks) with step1 display (simple props)
4. **Add an API call** → Use useEffect to fetch from /api/score
