# I Gave an AI a Research Goal and Went to Sleep. It Committed to Git 47 Times.

Not a demo. Not a controlled experiment. A real autonomous research agent running on free API keys, writing its own code, catching its own lies, and verifying its own results before it's allowed to stop.

---

## The Problem With AI Research Tools

Most AI research tools are glorified search bars. You ask, they answer, you copy-paste. The intelligence is yours — the AI just fetches.

That's not research. That's autocomplete with extra steps.

What I wanted was an agent that could take a goal, break it into criteria, write and run code to satisfy them, and not stop until the work was actually done — not just plausible-looking.

---

## How It Works

The agent reads a plain-English goal from `program.md`. Then it loops.

Each round it reads its own notes, writes Python, runs it via bash, saves results, and commits progress to git. The loop continues until every success criterion is checked off and independently verified.

No human in the loop. No babysitting. The git log tells the whole story.

---

## The Free Token Problem

Every free LLM tier has rate limits. One provider, one model — you hit the ceiling in minutes.

The solution is a rotating pool. `llm_router.py` treats every provider-model combination as an independent slot and round-robins across them. Groq, Gemini, OpenRouter — two accounts each, different models — and you have ten slots running in parallel rotation.

When one hits a rate limit, it sleeps. The others keep working. Effectively unlimited free inference for research workloads.

---

## The Hallucination Problem

The first version worked. It also lied.

The agent would do real work — download data, run backtests — and then write things like "this stock typically trades at a P/E of 18x" into its journal. Next round reads that as a verified fact. The entire research thread gets poisoned by a number that came from training data, not reality.

I added a hallucination guard on every journal write. Patterns like "approximately", "studies show", "I believe", "according to industry reports" trigger a warning. The agent must verify each flagged claim with a fresh bash command or web search before it can continue.

It also gets a pre-flight warning at the start of every round: anything suspicious from previous rounds is explicitly labeled a hypothesis until re-verified.

---

## The Verification Loop

The second problem: the agent would call done() too early.

It would check off criteria without proving anything, write a summary, and stop. The files existed. The numbers looked reasonable. But nothing had been re-executed.

Now after done() is accepted, the harness switches to verification mode. A different system prompt takes over — adversarial, skeptical. The agent re-runs every command. Re-reads every result file. Cross-checks key numbers.

If it finds issues, it fixes them and commits. The harness goes back to work mode. If everything checks out, it calls done() again. Only then does the run truly stop.

The architecture:

```
Round N   [WORK]   -> done() accepted by judge
Round N+1 [VERIFY] -> re-execute everything
           |-- done() again -> truly finished
           +-- git_commit() -> back to work
```

---

## Actionable Takeaways

**1. Rate limits are a routing problem, not a cost problem.**
Before paying for API access, exhaust the free tier across multiple providers and accounts. The infrastructure to rotate across them is less than 300 lines of Python.

**2. The agent's memory is a liability without citation rules.**
If you let an LLM write its own notes freely, it will mix verified outputs with training-data guesses and future rounds can't tell the difference. Force a convention: every factual claim must cite the command that produced it.

---

## Get the Code

Everything is open source: [github.com/30Signals/autoresearch](https://github.com/30Signals/autoresearch)

Fork it, write a `program.md`, point it at your free API keys, and watch it work through the night.

---

The best research doesn't come from asking better questions. It comes from building systems that won't let you stop at a plausible answer.
