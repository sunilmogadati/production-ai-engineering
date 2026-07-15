# Prompt Engineering: Setup & Quick Start

Get your Anthropic API key and run your first script in 5 minutes.

## Step 1: Get an API Key

1. Go to https://console.anthropic.com
2. Sign up or log in
3. Click **"API Keys"** in the left sidebar
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-`)
6. Save it somewhere safe (you'll only see it once)

## Step 2: Install the SDK

```bash
pip install anthropic
```

Verify it worked:
```bash
python -c "from anthropic import Anthropic; print('✓ SDK installed')"
```

## Step 3: Set Your API Key

Your code reads the key from the `ANTHROPIC_API_KEY` environment variable.

### macOS / Linux

```bash
# Option 1: Set it for this terminal session only
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"

# Then run a script
python prompt01_hello_world.py
```

### Windows (PowerShell)

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
python prompt01_hello_world.py
```

### Persistent (all future sessions)

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`, or `.env`):

```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### Or use a `.env` file (recommended for development)

Create a file called `.env` in the `fastapi-hello` directory:

```
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
```

Then load it in your script:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)
```

Install python-dotenv if needed:
```bash
pip install python-dotenv
```

## Step 4: Run Your First Script

```bash
cd /Users/sunilmogadati/Downloads/fastapi-hello
python prompt01_hello_world.py
```

You should see Claude's response in your terminal. If you do, you're set up! 🎉

## Step 5: Run the Progression

```bash
python prompt02_conversation.py
python prompt03_system_prompt.py
python prompt04_structured_output.py
python prompt05_temperature.py
```

Each takes ~5-10 seconds to run. Watch the output and read the comments.

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
You haven't installed the SDK yet.
```bash
pip install anthropic
```

### "401 Unauthorized" or "Invalid API key"
Your API key is wrong or not set. Check:
```bash
echo $ANTHROPIC_API_KEY  # Should print your key
```

If it's blank, set it:
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"
```

### "Rate limit exceeded"
You're sending too many requests too fast. Wait a minute and try again.
(Free tier has lower limits; paid tiers are higher.)

### Script hangs or takes forever
Claude is thinking (or the API is slow). Increase `max_tokens` to see partial responses:
```python
max_tokens=100,  # Smaller = faster (but truncated)
```

## Cost

**Free tier:**
- Free credits for your first month
- Read the console to see your usage

**Paid tier:**
- Input tokens: ~$0.003 per 1K tokens
- Output tokens: ~$0.015 per 1K tokens
- Example: a 500-token conversation costs ~$0.01 (one penny)

**Monitor your usage:**
- Go to https://console.anthropic.com/account/usage
- Set spending limits to be safe

## Key Environment Details

These scripts use:
- **Model:** `claude-3-5-sonnet-20241022` (latest, fastest, good balance of speed and quality)
- **API Version:** See https://docs.anthropic.com/en/docs/about/models for current models

If you want to experiment with different models:
```python
# Stronger but slower
model="claude-opus-4-8-20250514"

# Faster but less capable
model="claude-haiku-4-5-20251001"
```

See https://docs.anthropic.com/en/docs/about/models for the full list.

## Quick Reference

| Task | Model | Temperature | Max Tokens |
|------|-------|-------------|-----------|
| Chat / Q&A | Sonnet | 1 | 200-500 |
| JSON extraction | Sonnet | 0 | 1000 |
| Creative writing | Sonnet | 1.5 | 2000+ |
| Code review | Opus | 0 | 4000 |
| Fast inference | Haiku | 0-1 | 100-500 |

## What's Next

After setup, start with:
1. **prompt01_hello_world.py** (2 min)
2. **prompt02_conversation.py** (5 min)
3. **prompt03_system_prompt.py** (5 min)

See [PROMPT_PROGRESSION.md](PROMPT_PROGRESSION.md) for the full teaching series.

## Help

- Docs: https://docs.anthropic.com
- API Reference: https://docs.anthropic.com/en/api
- Discord (community): https://discord.gg/anthropic
