# CLAUDE.md — Project Context for Claude Code

## What this project is

An autonomous AI research agent. `harness.py` drives an LLM in a tool-calling loop to read a goal, write and run Python code, and commit results to git — round by round. `llm_router.py` rotates across free-tier LLM providers to avoid rate limits.

## Key files

| File | Purpose |
|---|---|
| `harness.py` | Orchestrator: round loop, tool dispatch, CLI |
| `llm_router.py` | Free LLM router: round-robin, cooldowns, retry |
| `llm_router_config.json` | Live config with API keys — **gitignored**, never commit |
| `llm_router_config.json.example` | Template — committed, no real keys |
| `experiments/<name>/program.md` | Research goal for that experiment |
| `experiments/<name>/evals/criteria.md` | Success criteria (agent-written) |
| `experiments/<name>/journal.md` | Agent's running notes (agent-written) |
| `experiments/<name>/results/` | All outputs: CSVs, plots, reports |

## Architecture decisions

- **`chdir` into experiment folder**: harness `os.chdir()`s into the experiment dir so all agent tool calls (`write_file`, `read_file`, `bash`) use relative paths naturally. Git still works because it traverses up to the repo root.
- **Slot expansion**: config stores provider × models list; router expands to flat slots for fine-grained round-robin (e.g. 2 OpenRouter keys × 3 models each = 6 independent slots).
- **BadRequestError handling**: decommissioned/unsupported model errors permanently disable that slot and rotate; other bad requests propagate to the harness.
- **Agent git commits**: use `--author="autoresearch <agent@autoresearch.local>"` to distinguish agent commits from human commits in `git log`.
- **Context window exceeded**: harness catches `ContextWindowExceededError`, trims to `messages[:1] + messages[-5:]`, and retries.

## Running

```bash
python harness.py --experiment experiments/nifty50-backtest
python harness.py --experiment experiments/nifty50-backtest --dry-run
```

## Adding a new experiment

```bash
mkdir experiments/<name>
# write experiments/<name>/program.md with the research goal
python harness.py --experiment experiments/<name>
```

## LLM config

`llm_router_config.json` is gitignored (contains API keys). The example file `llm_router_config.json.example` is committed. To verify all slots are working, run the inline test in the project history or craft a quick litellm call per slot.

Provider model IDs in config:
- **OpenRouter**: stored as `"deepseek/deepseek-chat:free"` — router prepends `openrouter/` at call time
- **Google**: stored as `"gemini/gemini-2.0-flash"` — used as-is by litellm
- **Groq**: stored as `"groq/llama-3.3-70b-versatile"` — used as-is by litellm (groq/ prefix required for non-standard model paths)

## What not to do

- Do not commit `llm_router_config.json` — it contains real API keys
- Do not commit `experiments/*/results/data/` — gitignored (raw data files)
- Do not add `results/` CSVs to git except `results/backtest_results.csv` (per .gitignore)
