# Setup — your laptop, your key

Two runtimes, because the ecosystem uses both: **Python** for agent and data work, **Node** for
app-layer and tooling work. Both are managed per-project so nothing lands in your system install.

Budget for this track: **a few dollars total.** Most builds run offline.

---

## 1. Python, with a virtual environment

A venv keeps this project's packages out of your system Python. Nothing here can break another
project, and deleting one folder undoes all of it.

```bash
python3 --version                 # need 3.10 or newer

git clone https://github.com/sunilmogadati/production-ai-engineering.git
cd production-ai-engineering

python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
```

Your prompt now shows `(.venv)`. That is how you know you are inside it. New terminal later? Run
`source .venv/bin/activate` again. Done for the day? `deactivate`.

```bash
pip install --upgrade pip
pip install anthropic
```

**Prefer `uv`?** It builds the environment for you and needs no activation:

```bash
uv run --with anthropic python builds/00-foundations/steps/01_hello.py
```

## 2. Node, with nvm

`nvm` installs Node **per user, per version** — no `sudo`, no fighting a system Node, and a
`.nvmrc` pins the version per project.

```bash
# install nvm (macOS / Linux)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# reopen the terminal, or:
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"

nvm install 22          # current LTS
nvm use 22
node --version
```

Then, for the TypeScript sample:

```bash
cd builds/00-foundations/steps
npm install                       # installs @anthropic-ai/sdk and tsx locally
```

`npm install` writes to `node_modules/` inside that folder — nothing global.

> **Do you need Node at all?** Only for the TypeScript sample. Every build in this track is Python.
> Node is here because the wider ecosystem is split, and seeing the same harness pattern in two
> languages is the fastest way to see that the pattern is not the syntax.

## 3. Your API key

Get one at [console.anthropic.com](https://console.anthropic.com) → **API Keys** → **Create Key**.
Copy it immediately; it is not shown again.

**Set a spend limit while you are there.** Console → your workspace → set a monthly cap. This track
costs cents, but an agent loop with a bug and no cap is the one genuinely expensive mistake in this
field. The cap turns it into a non-event.

### Where to put it

**A — Shell (local work).** Per terminal window:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Permanent — add that line to `~/.zshrc` (macOS) or `~/.bashrc` (Linux), then `source ~/.zshrc`.

**B — A `.env` file (per project).** Copy `.env.example` to `.env` and fill it in. `.env` is
gitignored; **`.env.example` carries names only, never values.**

**C — Google Colab.** Click the 🔑 in the left sidebar → **Add new secret** → name it exactly
`ANTHROPIC_API_KEY` → paste the value → switch on **Notebook access**.

Then read it with:

```python
from google.colab import userdata
import os
os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
```

Set once, and every future notebook picks it up. This is better than typing it into a cell: a
secret survives a runtime restart, and it never becomes part of the saved notebook — so a shared or
committed copy carries no credential. The track notebooks already resolve
**Colab Secrets → environment → prompt**, so B works there too.

### What you do NOT need

- **No `base_url`.** That is only for a proxy. With your own key the SDK talks to Anthropic directly.
- **No hosted classroom workspace.** A hosted workspace is a proxy with a scoped key — it changes
  one line and usually offers an older model list.
- **No key in your code.** `anthropic.Anthropic()` reads the environment by itself.

```python
import anthropic
client = anthropic.Anthropic()     # that is the entire setup
```

## 4. Verify

```bash
python3 builds/00-foundations/steps/01_hello.py
```

Expected: a model id, a one-line answer, token counts, and a cost of roughly $0.0001.

Optional, if you installed Node:

```bash
cd builds/00-foundations/steps && npx tsx 01_hello.ts
```

Same call, same shape, different syntax. That is the point of running both once.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ANTHROPIC_API_KEY is not set` | The `export` did not take, or you are in a different terminal. Run it again here. |
| `command not found: pip` | Use `python3 -m pip install anthropic`. |
| `(.venv)` missing from the prompt | `source .venv/bin/activate` from the repo root. |
| `command not found: nvm` | Reopen the terminal, or `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"`. |
| `404 model not found` | A model id was edited. The ids in this repo are complete as written — no date suffix. |
| `401` | Key is wrong, revoked, or has a stray space. Re-copy from the Console. |
