/**
 * Step 01 (TypeScript) — the same call, the same shape.
 *
 * Run this once alongside the Python version. The imports differ, the casing
 * differs, and nothing else does: same client, same message shape, same content
 * blocks, same usage figures.
 *
 * That is the argument for learning the harness rather than the SDK. A loop, a
 * tool schema, a context budget and a configuration hierarchy are the same idea
 * in both languages -- the syntax around them is all that moved.
 *
 * Run:  npm install && npx tsx 01_hello.ts
 */

import Anthropic from "@anthropic-ai/sdk";

const MODEL = "claude-haiku-4-5";   // complete as written -- no date suffix
const RATE_IN = 1.0;                // $ per million tokens
const RATE_OUT = 5.0;

async function main(): Promise<void> {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("ANTHROPIC_API_KEY is not set.\n  export ANTHROPIC_API_KEY=sk-ant-...");
    process.exit(1);
  }

  // No apiKey, no baseURL -- both resolve from the environment, as in Python.
  const client = new Anthropic();

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 200,
    system: "You explain engineering ideas to experienced developers. Two sentences, no preamble.",
    messages: [{ role: "user", content: "What does an LLM harness do that the model does not?" }],
  });

  const answer = response.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("");

  const { input_tokens: inTok, output_tokens: outTok } = response.usage;
  const cost = (inTok * RATE_IN + outTok * RATE_OUT) / 1_000_000;

  console.log(`\n  model : ${response.model}`);
  console.log(`  stop  : ${response.stop_reason}`);
  console.log(`\n  ${answer.trim()}\n`);
  console.log(`  tokens: in=${inTok}  out=${outTok}`);
  console.log(`  cost  : $${cost.toFixed(6)}`);
  console.log("\n  Same call, same shape, different syntax. That is the point.\n");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
