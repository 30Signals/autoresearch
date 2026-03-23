# autoresearch

An autonomous AI research agent that reads a goal from `program.md`, writes its own code, runs experiments, self-evaluates, and commits results to git — round by round.

It uses a **free token router** (`llm_router.py`) that rotates across multiple LLM providers (OpenRouter, Gemini, Groq) to get effectively unlimited free inference.

## How it works

1. You write a research goal in `experiments/<name>/program.md`
2. The agent runs in a loop:
   - **Round 1**: reads the goal, creates `evals/criteria.md` with measurable success criteria
   - **Every round**: reads `journal.md` for context, writes/runs Python code, appends findings to `journal.md`, commits progress with `git_commit()`
   - **Final round**: calls `done()` when all criteria are met, writes `results/SUMMARY.md`
3. All outputs (CSVs, plots, reports) go into `experiments/<name>/results/`

## Structure

```
autoresearch/
├── harness.py                      # main orchestrator — run this
├── llm_router.py                   # reusable free LLM router
├── llm_router_config.json.example  # copy to ~/.llm_router_config.json or project root
├── requirements.txt
├── experiments/
│   └── nifty50-backtest/           # example experiment
│       ├── program.md              # research goal
│       ├── evals/criteria.md       # success criteria (agent-written)
│       ├── journal.md              # agent's running notes (agent-written)
│       └── results/                # outputs: CSVs, plots, reports
└── .env.example
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure LLM providers
cp llm_router_config.json.example llm_router_config.json
# edit llm_router_config.json with your API keys
# (or copy to ~/.llm_router_config.json to share across projects)
```

### Getting free API keys

| Provider | Where | Notes |
|---|---|---|
| OpenRouter | [openrouter.ai](https://openrouter.ai) | Many `:free` models; create multiple accounts to multiply slots |
| Google AI Studio | [aistudio.google.com](https://aistudio.google.com) | Gemini 2.0 Flash free tier |
| Groq | [console.groq.com](https://console.groq.com) | Fast inference, free tier |

## Usage

```bash
# Run an experiment
python harness.py --experiment experiments/nifty50-backtest

# Create and run a new experiment
mkdir experiments/my-research
echo "# Goal: ..." > experiments/my-research/program.md
python harness.py --experiment experiments/my-research

# Dry-run: preview context + tools without calling any LLM
python harness.py --experiment experiments/my-research --dry-run

# Other options
python harness.py --experiment experiments/my-research --max-rounds 5
python harness.py --experiment experiments/my-research --config /path/to/config.json
```

## Watching it run

```bash
# In separate terminals:
tail -f experiments/nifty50-backtest/journal.md   # agent's live notes
git log --oneline                                  # commits after each round
```

## LLM Router

`llm_router.py` is a standalone module you can copy into any project. It:

- Expands each provider × model into a flat slot list for fine-grained round-robin
- Tracks per-slot cooldowns (rate limit → 60s, service unavailable → 30s, connection error → 10s)
- Permanently disables slots on auth errors or decommissioned models
- Waits automatically when all slots are cooling down

Config is loaded from (in order): explicit path → `~/.llm_router_config.json` → `./llm_router_config.json`

## Inspiration

Inspired by [Andrej Karpathy's autoresearch loop](https://github.com/karpathy/autoresearch/).

## License

MIT
