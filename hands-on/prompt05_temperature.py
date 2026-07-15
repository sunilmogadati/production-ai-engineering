#!/usr/bin/env python3
"""
Prompt Engineering 05: Temperature & Sampling

Temperature controls how "creative" or "random" Claude's responses are.
  - temperature=0 (default): deterministic, consistent, boring
  - temperature=1: balanced, creative but plausible
  - temperature=2: wild, unpredictable, fun but risky

Use temperature=0 for:
  ✓ Extracting facts (JSON, summaries, classifications)
  ✓ Code generation (you need it to run)
  ✓ Anything where you need reproducible results

Use temperature=1+ for:
  ✓ Creative writing (stories, jokes, marketing copy)
  ✓ Brainstorming (idea generation)
  ✓ Exploratory conversations

Run:
    python prompt05_temperature.py
"""

from anthropic import Anthropic

client = Anthropic()

# ============================================================================
# Example: Ask Claude to generate a product tagline
# ============================================================================
# Same prompt, different temperatures → different creativity levels

product = "A coffee mug that keeps your coffee hot for 8 hours"

prompt = f"""Generate a catchy, one-line product tagline for this:
{product}

Tagline (just the tagline, no explanation):"""

# ============================================================================
# Temperature 0: Consistent and conservative
# ============================================================================
print("=== Temperature 0 (deterministic) ===")
for i in range(3):
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=50,
        temperature=0,  # No randomness
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    print(f"  Run {i+1}: {response.content[0].text.strip()}")

print()

# ============================================================================
# Temperature 1: Balanced and creative
# ============================================================================
print("=== Temperature 1 (balanced) ===")
for i in range(3):
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=50,
        temperature=1,  # Balanced
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    print(f"  Run {i+1}: {response.content[0].text.strip()}")

print()

# ============================================================================
# Temperature 1.0: Maximum allowed (some models limit to 0-1)
# ============================================================================
print("=== Temperature 1.0 (max creative) ===")
for i in range(3):
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=50,
        temperature=1.0,  # Maximum creativity (some models cap at 1.0)
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    print(f"  Run {i+1}: {response.content[0].text.strip()}")

print()

# ============================================================================
# Notice: temp=0 is nearly identical. temp=1+ is varied.
# ============================================================================
# This shows temperature's effect:
#   Low temp: same answer every time (good for deterministic tasks)
#   High temp: different answers each time (good for creative brainstorming)

# ============================================================================
# Other sampling parameters (advanced)
# ============================================================================
# top_p (nucleus sampling): probability mass to consider
#   top_p=0.1: only the top 10% most likely tokens (conservative)
#   top_p=0.9: top 90% of the distribution (creative)
#
# This is an alternative to temperature. Most of the time, just use temperature.
