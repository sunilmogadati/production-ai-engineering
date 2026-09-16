# Setup — 5 minutes, before Lesson 01

You need three things: Python, this repository, and an API key. Nothing is installed globally
and nothing here costs more than a few cents to run.

## 1. Check Python

```bash
python3 --version
```

**3.10 or newer.** If that command fails or shows something older, install Python 3 from
[python.org](https://www.python.org/downloads/) and reopen your terminal.

## 2. Get the code

```bash
git clone https://github.com/sunilmogadati/production-ai-engineering.git
cd production-ai-engineering/builds/01-model-routing
```

## 3. Run something right now — no key needed

```bash
cd src && python3 bench.py
```

You should see a table of seven configurations with costs. **If that printed, you are set up**
for half the lesson — the cost analysis is pure arithmetic and needs no API access at all.

Come back up a level when you're done: `cd ..`

## 4. Get an API key

**If you are running the [Colab notebook](https://colab.research.google.com/github/sunilmogadati/production-ai-engineering/blob/main/notebooks/hello_model_selection.ipynb)**, you do not need steps 1–3 at all —
get a key below, then click the 🔑 in Colab's left sidebar, **Add new secret**, name it exactly
`ANTHROPIC_API_KEY`, and switch on **Notebook access**. Done once, it works in every notebook after.

### Getting one

1. Go to [console.anthropic.com](https://console.anthropic.com) and sign in or create an account.
2. Add a small amount of credit — **$5 is more than enough**; this lesson costs a few cents.
3. Go to **API Keys** → **Create Key**. Copy it immediately; you cannot view it again.

Set it in your terminal:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

That lasts for this terminal session only. To make it permanent, add the same line to your
`~/.zshrc` (macOS) or `~/.bashrc` (Linux).

**Never paste a key into a file you commit, a chat, or a screen share.** If one leaks, revoke it in
the console immediately — that is what the revoke button is for, and everyone does it eventually.

## 5. Install the SDK and verify

```bash
pip install anthropic
cd steps && python3 01_one_call.py
```

Expected: one word of output, plus token counts and a cost of roughly $0.00001.

**If you see `ANTHROPIC_API_KEY is not set`** — the export didn't take. Run it again in the same
terminal window you're using now.

**If you see `pip: command not found`** — try `python3 -m pip install anthropic`.

**If you'd rather not install into your system Python:**

```bash
uv run --with anthropic python 01_one_call.py
```

## You're ready

| What | Command | Needs a key |
|---|---|---|
| The offline bench | `cd src && python3 bench.py` | no |
| The five steps | `cd steps && python3 01_one_call.py` | yes |
| The lesson | [LESSON.md](LESSON.md) | — |

Total spend if you run every step in this lesson: **well under $1.**
