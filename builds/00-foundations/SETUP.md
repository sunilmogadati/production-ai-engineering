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

# Name the interpreter explicitly -- do NOT rely on bare `python3`, and do not
# run this while another venv is active. Both break venvs in confusing ways.
$(brew --prefix)/bin/python3.12 -m venv .venv     # macOS; any python3.10+ you trust
source .venv/bin/activate         # Windows: .venv\Scripts\activate
```

> `python3` may be a version manager's shim, which resolves at call time rather than pointing at a
> fixed binary. A venv built on a shim can end up with `pip` and `python` serving different Python
> versions — installs succeed, then the import fails. `/usr/bin/python3` on macOS is 3.9, too old.

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

**Why nvm and not a plain Node install.** `nvm` puts Node under your home directory, one copy per
version. No `sudo`, no fighting a system Node another tool installed, and a `.nvmrc` file pins the
version per project so two projects can want different Node versions and both get them.

### 2.1 Install nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

The installer appends a block to your shell profile. On macOS that is `~/.zshrc`; on most Linux
shells `~/.bashrc`.

### 2.2 Make the current shell see it

The installer does not change the shell you are already in. Either **open a new terminal**, or:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

Check it worked:

```bash
command -v nvm        # prints: nvm
```

**If that prints nothing**, the profile block did not land. Add it yourself to `~/.zshrc`:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

then `source ~/.zshrc`.

> `nvm` is a **shell function**, not a binary. `which nvm` will fail even when it is working —
> use `command -v nvm`.

### 2.3 Install Node and make it the default

```bash
nvm install --lts          # installs the current LTS and switches to it
nvm alias default 'lts/*'  # every new terminal starts on it
```

Verify:

```bash
node --version             # v22.x or newer
npm --version
```

### 2.4 Per-project version pinning

Each of our Node folders carries a `.nvmrc` naming the version it expects:

```bash
cd builds/00-foundations/steps
cat .nvmrc                 # 22
nvm use                    # reads .nvmrc and switches
```

**Optional but worth it — switch automatically on `cd`.** Add to `~/.zshrc`:

```bash
autoload -U add-zsh-hook
load-nvmrc() { [ -f .nvmrc ] && nvm use --silent >/dev/null 2>&1; }
add-zsh-hook chpwd load-nvmrc
load-nvmrc
```

Now `cd` into a project and the right Node is selected without you thinking about it.

### 2.5 Install this folder's packages

```bash
cd builds/00-foundations/steps
npm install                # writes ./node_modules -- nothing global
npx tsx 01_hello.ts
```

`npx tsx` runs TypeScript directly, with no build step and no `tsc` output to manage.

### Useful nvm commands

| Command | Does |
|---|---|
| `nvm ls` | versions installed, and which is active |
| `nvm ls-remote --lts` | what is available |
| `nvm use 22` | switch this shell to 22 |
| `nvm use` | switch to whatever `.nvmrc` says |
| `nvm alias default 'lts/*'` | what new shells start with |
| `nvm uninstall 20` | remove a version |

### Do you need Node at all?

**No — every build in this track is Python.** Node is here for the TypeScript twins of a couple of
steps, so you can run the same harness pattern in both languages and see that the pattern is not the
syntax. Skip it and you lose nothing but that demonstration.

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

## 4. Verify — one command

```bash
cd <repo root> && python3 check_env.py
```

Eight checks: Python version, venv active, interpreter inside it, a single site-packages tree, no
shim in the chain, the SDK, your key, and the offline bench. No key or network required, and every
failure prints its fix.

## 5. Verify by running something

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
