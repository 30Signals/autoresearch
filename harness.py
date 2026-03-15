#!/usr/bin/env python3
"""
harness.py — Autonomous Research Agent Orchestrator

Reads program.md, writes code, runs experiments, generates evals,
and commits to git after each round.

Usage:
    python harness.py                        # run research
    python harness.py --dry-run              # print context + tools schema, exit
    python harness.py --config path/to/cfg   # override config path
    python harness.py --max-rounds N         # override max rounds
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from litellm.exceptions import ContextWindowExceededError

from llm_router import LLMRouter

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an autonomous research agent and software engineer.

Rules:
- Round 1: read program.md, create evals/criteria.md with measurable success criteria
- Every round: read journal.md to recall progress
- Write Python with write_file(), run it with bash()
- Append findings to journal.md every round (read first, then write full content)
- Call git_commit("msg") when you've made meaningful progress — this ends the round
- Call done("summary") when ALL success criteria are met
- Never ask for confirmation — make decisions and execute
- Debug failures in the same round; don't give up
- Save all results (CSV, plots) to results/
"""

# ---------------------------------------------------------------------------
# Tool definitions (OpenAI function-call format)
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command. Returns stdout+stderr (last 5000 chars).",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default 60)", "default": 60},
                },
                "required": ["cmd"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file (creates parent directories).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Text content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file's text content (last 8000 chars if large).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files/directories at a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list (default: .)", "default": "."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage all changes and commit. Ends the current round.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Signal that all success criteria are met. Ends research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Summary of research results"},
                },
                "required": ["summary"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_bash(cmd: str, timeout: int = 60) -> str:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        if len(output) > 5000:
            output = "...[truncated]...\n" + output[-5000:]
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"


def tool_write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} chars to {path}"
    except Exception as e:
        return f"ERROR: {e}"


def tool_read_file(path: str) -> str:
    try:
        p = Path(path)
        if not p.exists():
            return f"ERROR: File not found: {path}"
        content = p.read_text(encoding="utf-8")
        if len(content) > 8000:
            content = "...[truncated to last 8000 chars]...\n" + content[-8000:]
        return content
    except Exception as e:
        return f"ERROR: {e}"


def tool_list_files(path: str = ".") -> str:
    try:
        p = Path(path)
        if not p.exists():
            return f"ERROR: Path not found: {path}"
        entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        lines = []
        for entry in entries:
            prefix = "f" if entry.is_file() else "d"
            lines.append(f"{prefix} {entry.name}")
        return "\n".join(lines) if lines else "(empty directory)"
    except Exception as e:
        return f"ERROR: {e}"


def tool_git_commit(message: str) -> str:
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit",
             "--author=autoresearch <agent@autoresearch.local>",
             "-m", message],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return f"Committed: {message}\n{result.stdout}"
        elif "nothing to commit" in result.stdout + result.stderr:
            return "Nothing to commit (working tree clean)"
        else:
            return f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {e}"


def tool_done(summary: str) -> str:
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    summary_path = results_dir / "SUMMARY.md"
    summary_path.write_text(f"# Research Summary\n\n{summary}\n", encoding="utf-8")
    return f"Research marked complete. Summary saved to results/SUMMARY.md"


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------
TOOL_DISPATCH = {
    "bash": tool_bash,
    "write_file": tool_write_file,
    "read_file": tool_read_file,
    "list_files": tool_list_files,
    "git_commit": tool_git_commit,
    "done": tool_done,
}


def execute_tool(name: str, args: dict) -> str:
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return f"ERROR: Unknown tool: {name}"
    try:
        return fn(**args)
    except Exception as e:
        return f"ERROR executing {name}: {e}"


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context() -> str:
    program = tool_read_file("program.md")
    criteria_path = Path("evals/criteria.md")
    if criteria_path.exists():
        criteria = criteria_path.read_text(encoding="utf-8")
    else:
        criteria = "(not yet created — create in round 1)"

    journal_path = Path("journal.md")
    if journal_path.exists():
        journal_content = journal_path.read_text(encoding="utf-8")
        if len(journal_content) > 12000:
            journal_content = "...[truncated to last 12000 chars]...\n" + journal_content[-12000:]
    else:
        journal_content = "(empty — this is round 1)"

    return f"""\
## PROGRAM (your goal)
{program}

## SUCCESS CRITERIA
{criteria}

## JOURNAL (your progress log)
{journal_content}
"""


# ---------------------------------------------------------------------------
# Git configuration
# ---------------------------------------------------------------------------

def ensure_git_configured():
    def git_get(key):
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    if not git_get("user.email"):
        subprocess.run(["git", "config", "user.email", "autoresearch@agent.local"], check=True)
    if not git_get("user.name"):
        subprocess.run(["git", "config", "user.name", "autoresearch"], check=True)


# ---------------------------------------------------------------------------
# Response processing
# ---------------------------------------------------------------------------

def process_response(response) -> tuple[list, dict]:
    msg = response.choices[0].message

    # Guard: some models return empty list on finish_reason="tool_calls"
    tool_calls_raw = msg.tool_calls if msg.tool_calls and len(msg.tool_calls) > 0 else []

    # Build assistant message preserving tool_call IDs
    asst_msg = {
        "role": "assistant",
        "content": msg.content or "",
    }
    if tool_calls_raw:
        asst_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in tool_calls_raw
        ]

    tool_calls = [
        {
            "id": tc.id,
            "name": tc.function.name,
            "args": json.loads(tc.function.arguments),
        }
        for tc in tool_calls_raw
    ]

    return tool_calls, asst_msg


def make_tool_result_message(tool_call_id: str, result: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": result,
    }


# ---------------------------------------------------------------------------
# Main research loop
# ---------------------------------------------------------------------------

def run_research(config_path=None, max_rounds=None, max_tool_calls_per_round=None):
    if not Path("program.md").exists():
        print("ERROR: program.md not found. Create it first.")
        sys.exit(1)

    ensure_git_configured()
    router = LLMRouter(config_path=config_path)

    # Load limits from config or use defaults
    cfg = router._config
    effective_max_rounds = max_rounds or cfg.get("max_rounds", 20)
    effective_max_tools = max_tool_calls_per_round or cfg.get("max_tool_calls_per_round", 50)

    print(f"Starting research: max_rounds={effective_max_rounds}, max_tool_calls={effective_max_tools}")

    for round_num in range(effective_max_rounds):
        print(f"\n{'='*60}")
        print(f"=== Round {round_num + 1} / {effective_max_rounds} ===")
        print(f"{'='*60}")

        context = build_context()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]

        round_done = False
        research_done = False
        nudge_count = 0

        for tool_call_num in range(effective_max_tools):
            try:
                response = router.chat_with_tools(messages, TOOLS)
            except ContextWindowExceededError:
                print("  [harness] Context window exceeded — trimming messages...")
                messages = messages[:1] + messages[-5:]
                continue

            tool_calls, asst_msg = process_response(response)
            messages.append(asst_msg)

            if not tool_calls:
                nudge_count += 1
                if nudge_count >= 2:
                    print("  [harness] No tool calls after nudge — ending round")
                    break
                messages.append({
                    "role": "user",
                    "content": (
                        "You generated text but called no tools. "
                        "Call git_commit() to end this round, or done() if all criteria are met."
                    ),
                })
                continue

            nudge_count = 0  # reset on successful tool call

            for tc in tool_calls:
                result = execute_tool(tc["name"], tc["args"])
                preview = result[:120].replace("\n", " ")
                print(f"  [{tc['name']}] → {preview}")
                messages.append(make_tool_result_message(tc["id"], result))

                if tc["name"] == "git_commit":
                    round_done = True
                if tc["name"] == "done":
                    research_done = True

            if round_done or research_done:
                break

        if research_done:
            print("\n[harness] Research complete! Auto-committing any remaining changes...")
            subprocess.run(["git", "add", "-A"])
            subprocess.run([
                "git", "commit",
                "--author=autoresearch <agent@autoresearch.local>",
                "-m", "auto-commit: research complete", "--allow-empty"
            ])
            print("[harness] Done.")
            return

    print(f"\n[harness] Reached max rounds ({effective_max_rounds}). Research loop ended.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Autoresearch — Autonomous Research Agent"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print context and tools schema, then exit")
    parser.add_argument("--config", default=None,
                        help="Path to llm_router_config.json")
    parser.add_argument("--max-rounds", type=int, default=None,
                        help="Override max rounds from config")
    parser.add_argument("--max-tool-calls", type=int, default=None,
                        help="Override max tool calls per round from config")
    parser.add_argument("--experiment", default=None, metavar="DIR",
                        help="Path to experiment folder (contains program.md). Created if missing.")
    args = parser.parse_args()

    if args.experiment:
        exp_path = Path(args.experiment).resolve()
        exp_path.mkdir(parents=True, exist_ok=True)
        os.chdir(exp_path)
        print(f"[harness] Experiment dir: {exp_path}")

    if args.dry_run:
        print("=== DRY RUN ===\n")
        print("--- Context (would be sent as first user message) ---\n")
        print(build_context())
        print("\n--- Tools Schema ---\n")
        print(json.dumps(TOOLS, indent=2))
        print("\n--- System Prompt ---\n")
        print(SYSTEM_PROMPT)
        return

    run_research(
        config_path=args.config,
        max_rounds=args.max_rounds,
        max_tool_calls_per_round=args.max_tool_calls,
    )


if __name__ == "__main__":
    main()
