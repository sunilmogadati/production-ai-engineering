#!/usr/bin/env python3
"""
Prompt Engineering 01: Hello World

The simplest possible introduction to the Anthropic API.
This script:
  1. Imports the Anthropic client
  2. Creates a message using Claude
  3. Prints the response

That's it. No fancy patterns, no error handling, no async.
Just: request → response → print.

Run this after installing the SDK:
    pip install anthropic

Then:
    python prompt01_hello_world.py
"""

from anthropic import Anthropic

# ============================================================================
# STEP 1: Create the client
# ============================================================================
# The Anthropic() constructor reads ANTHROPIC_API_KEY from your environment.
# Make sure you have it set:
#   export ANTHROPIC_API_KEY="sk-ant-..."
#
# The client is reusable for many requests. You only create it once.
client = Anthropic()

# ============================================================================
# STEP 2: Send a message and get a response
# ============================================================================
# client.messages.create() is the core API call.
# It takes:
#   model: which Claude model to use (see https://docs.anthropic.com/en/docs/about/models)
#   max_tokens: maximum length of Claude's response (1-4096)
#   messages: list of message dicts with role ("user" or "assistant") and content
#
# The response is a Message object with:
#   - content: list of content blocks (usually just one TextBlock)
#   - stop_reason: why Claude stopped ("end_turn", "max_tokens", etc.)
#   - usage: token counts
#
response = client.messages.create(
    model="claude-opus-4-1",  # Latest model available
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Say hello and explain what you are in one sentence.",
        }
    ],
)

# ============================================================================
# STEP 3: Extract and print the response
# ============================================================================
# response.content[0] is the first (and usually only) content block.
# For text responses, it's a TextBlock with a .text attribute.
#
# In a real app, you'd check response.stop_reason and response.usage,
# but for hello world, we just print the text.
print("Claude says:")
print(response.content[0].text)

# ============================================================================
# What's next?
# ============================================================================
# Now that you can call the API, the next scripts show:
#   prompt02: Multi-turn conversation (remembering context)
#   prompt03: System prompts (instructions for Claude)
#   prompt04: Extracting structured data (JSON)
#   prompt05: Temperature & sampling (creativity vs. consistency)
#   prompt06: Token counting (measure cost before you pay)
#   prompt07: Streaming (real-time responses)
#   ...and more
