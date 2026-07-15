#!/usr/bin/env python3
"""
Prompt Engineering 03: System Prompts

A "system prompt" is Claude's instructions—separate from the conversation.
It's like telling Claude: "You are a Shakespearean translator" BEFORE
any user messages. Then the user says "Translate 'hello' to Shakespeare"
and Claude knows what role to play.

Key difference from prompt02:
  prompt02: messages = [user msg, assistant reply, user msg, ...]
  prompt03: system = instructions + messages = [user msg, assistant reply, ...]

Run:
    python prompt03_system_prompt.py
"""

from anthropic import Anthropic

client = Anthropic()

# ============================================================================
# Example 1: Sales coach persona
# ============================================================================
print("=== Example 1: Sales Coach ===\n")

messages = []

def chat_with_system(user_message, system_prompt):
    """
    Send a message with a system prompt (role/instructions).
    System prompt tells Claude who it is and how to behave.
    """
    messages.append({
        "role": "user",
        "content": user_message,
    })

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=300,
        system=system_prompt,  # NEW! This is the system prompt
        messages=messages,
    )

    assistant_message = response.content[0].text
    messages.append({
        "role": "assistant",
        "content": assistant_message,
    })

    return assistant_message

# Tell Claude to act as a sales coach
sales_coach_system = """You are an expert sales coach with 20 years of experience.
Your job is to help salespeople improve their techniques, close more deals,
and build better relationships. Be direct, practical, and use real examples.
Always ask clarifying questions before giving advice."""

response = chat_with_system(
    "I struggle with objection handling. Any tips?",
    sales_coach_system,
)
print(f"Coach: {response}\n")

# The user continues the conversation
response = chat_with_system(
    "What if they say 'I need to think about it'?",
    sales_coach_system,
)
print(f"Coach: {response}\n")

# ============================================================================
# Example 2: Same question, different system prompt
# ============================================================================
print("\n=== Example 2: Comedian (same question) ===\n")

# Reset the conversation history
messages = []

comedian_system = """You are a stand-up comedian who finds humor in everything,
especially everyday business situations. Respond to every question with jokes,
wordplay, and funny observations. Keep it light and entertaining."""

response = chat_with_system(
    "I struggle with objection handling. Any tips?",
    comedian_system,
)
print(f"Comedian: {response}\n")

# ============================================================================
# Example 3: A teacher system prompt
# ============================================================================
print("\n=== Example 3: Teacher (same question) ===\n")

messages = []

teacher_system = """You are a patient, encouraging teacher. Explain concepts
using simple language, real-world analogies, and step-by-step breakdowns.
Always assume the student is smart but new to the topic. Use examples."""

response = chat_with_system(
    "I struggle with objection handling. Any tips?",
    teacher_system,
)
print(f"Teacher: {response}\n")

# ============================================================================
# Key learning: System prompt shapes everything
# ============================================================================
# Same user question → completely different answers depending on system prompt.
#
# System prompt uses: role/persona, tone, constraints, goals, context
#   ✓ "You are a Shakespearean translator"
#   ✓ "Be concise and use technical jargon"
#   ✓ "Only respond if you're 90% confident; say 'I don't know' otherwise"
#   ✓ "Extract the JSON from the user's input"
#
# System prompt does NOT change between turns (unlike messages).
# It's the standing instructions for the whole conversation.
