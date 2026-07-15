#!/usr/bin/env python3
"""
Prompt Engineering 02: Multi-Turn Conversation

Build on prompt01 by having a real conversation.
Claude remembers what you said before (as long as you send the full history).

Key new concept: the message history is YOURS to manage.
You keep a list of all messages (user + assistant), and send the whole
thing each time. Claude doesn't have memory—you do.

Run:
    python prompt02_conversation.py
"""

from anthropic import Anthropic

# Create the client (same as before)
client = Anthropic()

# ============================================================================
# STEP 1: Initialize conversation history
# ============================================================================
# This is a list of message dicts. Each time we call the API,
# we send the ENTIRE history. Claude uses it for context.
# After each response, we append Claude's reply to this list.
messages = []

# ============================================================================
# STEP 2: Helper function for a single turn
# ============================================================================
def chat(user_message):
    """
    Send one message and get one response.
    Appends both to the history so the next call has context.
    """
    # Add the user's message to the history
    messages.append({
        "role": "user",
        "content": user_message,
    })

    # Call the API with the full history
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=200,
        messages=messages,  # Full history (not just the latest message!)
    )

    # Extract Claude's response
    assistant_message = response.content[0].text

    # Add Claude's response to the history
    messages.append({
        "role": "assistant",
        "content": assistant_message,
    })

    return assistant_message

# ============================================================================
# STEP 3: Have a conversation
# ============================================================================
# Each call to chat() appends to messages[], so Claude has context.
# Try it: change the questions and watch Claude remember.

print("Turn 1:")
response = chat("My favorite color is blue. What does that say about me?")
print(f"Claude: {response}\n")

print("Turn 2:")
response = chat("Does that apply to other colors too?")
print(f"Claude: {response}\n")

print("Turn 3:")
response = chat("What color do you think suits me?")
print(f"Claude: {response}\n")

# ============================================================================
# STEP 4: See the full history
# ============================================================================
# Uncomment to see what Claude saw:
# print("\n=== Full conversation history ===")
# for msg in messages:
#     print(f"{msg['role'].upper()}: {msg['content']}\n")

# ============================================================================
# Key learning: Who manages history?
# ============================================================================
# You (the Python script) manage it. Each turn:
#   1. You add the user message to the list
#   2. You send the full list to Claude
#   3. Claude responds (it doesn't "remember" anything)
#   4. You add Claude's response to the list
#   5. Next turn: repeat
#
# If you DON'T send the history, Claude thinks it's a new conversation.
# If you MUTATE the history wrong (delete/reorder), Claude gets confused.
#
# In a real app: this list lives in memory (fast), or a database
# (so you can resume conversations later).
