#!/usr/bin/env python3
"""
harness.py — Autonomous Research Agent Orchestrator

Reads program.md, writes code, runs experiments, generates evals,
and commits to git after each round.

Usage:
    python harness.py                        # run research
    python harness.py --continue             # resume an interrupted run
    python harness.py --dry-run              # print context + tools schema, exit
    python harness.py --config path/to/cfg   # override config path
    python harness.py --max-rounds N         # override max rounds
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from litellm.exceptions import ContextWindowExceededError

from llm_router import LLMRouter

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an autonomous research agent and software engineer.

Rules:
- Round 1: read program.md, then create evals/criteria.md as a markdown checklist:
    - [ ] Each line is one concrete, verifiable deliverable
    - Use exactly this format: "- [ ] <criterion>" (unchecked) / "- [x] <criterion>" (done)
    - Be specific: filenames, metric names, thresholds — not vague goals
- Every round: read journal.md to recall progress, then work toward unchecked criteria
- Write Python with write_file(), run it with bash()
- After completing each criterion, update evals/criteria.md: change "- [ ]" to "- [x]"
- Append findings to journal.md every round (read first, then write full content)
- Call git_commit("msg") when you've made meaningful progress — this ends the round
- Before calling done(), you MUST run a verification pass in the same round:
    1. Re-read evals/criteria.md and list every checked criterion
    2. For each criterion, re-run or re-check the actual output (bash, read_file) to confirm it is real
    3. Only call done() after you have verified every criterion with fresh evidence — not from memory
  done() will be REJECTED and return the list of remaining unchecked criteria if any exist.
  Fix them before calling done() again.
- Never ask for confirmation — make decisions and execute
- Debug failures in the same round; don't give up
- Save all results (CSV, plots) to results/

CRITICAL — journal.md integrity rules (strictly enforced):
- Every factual claim (numbers, names, dates, stats, prices) MUST be followed by the exact
  bash() command output or web_search() result that verified it. No citation = not a fact.
- Mark unverified hypotheses explicitly: [HYPOTHESIS] <claim>
- NEVER write facts from memory or training data. If you didn't get it from bash() or
  web_search() in THIS session, it is a hypothesis, not a fact.
- If write_file("journal.md", ...) returns a HALLUCINATION WARNING, you MUST immediately
  verify each flagged claim with bash() or web_search() and rewrite the journal entry
  with proper citations before proceeding.

web_search() usage:
- Use web_search() to look up current facts, prices, data, and external information
- Always cite the query used: "web_search('...') returned: ..."
- Cross-check important numbers with a second search or bash() verification
"""

VERIFICATION_PROMPT = """\
You are an autonomous research agent in VERIFICATION MODE.

Your ONLY job this round is to independently verify that all claimed results are real and correct.
Do NOT do new research or add new features.

Verification steps (do all of these):
1. Read evals/criteria.md — list every criterion marked [x]
2. For each criterion: re-run the bash() command or web_search() that produced the evidence.
   Do not trust the journal — re-execute and confirm with fresh output.
3. Re-read every file in results/ and confirm contents match what criteria.md and journal.md claim.
4. Cross-check key numbers with a second web_search() where appropriate.

After verification:
- If everything checks out → call done() with a verification summary
- If you find any discrepancy or error → fix it, update journal.md with findings,
  call git_commit(), and the harness will run another round to address remaining issues.

Be skeptical. Treat every claim as unverified until you have re-executed it yourself.
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
            "name": "web_search",
            "description": (
                "Search the web using DuckDuckGo. Returns titles, URLs, and snippets. "
                "Use for current facts, prices, data, and external information. "
                "Always cite the query and results when writing to journal.md."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Max results to return (default 5)", "default": 5},
                },
                "required": ["query"],
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
            "description": (
                "Signal that all success criteria in evals/criteria.md are met. "
                "Will be REJECTED (returning remaining unchecked items) if any '- [ ]' lines exist. "
                "Update criteria.md to '- [x]' for each completed item before calling this."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Summary of research results and findings"},
                },
                "required": ["summary"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Hallucination detection
# ---------------------------------------------------------------------------

# Patterns that suggest a claim came from training memory rather than verified output
HALLUCINATION_PATTERNS = [
    (r'\b(approximately|roughly|around|about)\s+\d[\d,.]*\s*(%|percent|million|billion|thousand|crore|lakh)', "unverified number"),
    (r'\b(typically|usually|generally|often|commonly|normally)\b', "vague generalization"),
    (r'\bbased on (my|our) (knowledge|training|understanding|experience)\b', "training memory reference"),
    (r'\bI (believe|think|know|recall|remember)\b', "unverified personal belief"),
    (r'\baccording to (?!the (bash|command|output|result|above|following|web_search))', "uncited source"),
    (r'\b(studies|research|reports?|data)\s+(show|indicate|suggest|find|confirm)\b', "uncited study/report"),
    (r'\bhistorically\b', "historical claim without source"),
    (r'\bin (my|our) experience\b', "experiential claim"),
    (r'\bI (have seen|have found|have noticed|have observed)\b', "unverified observation"),
    (r'\bas of \d{4}\b', "potentially stale date"),
]


def check_for_hallucinations(content: str) -> list:
    """Scan journal content for uncited claims. Returns list of warning strings."""
    warnings = []
    for i, line in enumerate(content.splitlines(), 1):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue
        for pattern, label in HALLUCINATION_PATTERNS:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                warnings.append(f"Line {i} [{label}]: {line_stripped[:120]}")
                break  # one warning per line
    return warnings


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
        result = f"Written {len(content)} chars to {path}"

        # Post-write hallucination check for journal.md
        if Path(path).name == "journal.md":
            warnings = check_for_hallucinations(content)
            if warnings:
                warning_lines = "\n".join(f"  - {w}" for w in warnings[:15])
                result += (
                    f"\n\n⚠️  HALLUCINATION WARNING — {len(warnings)} suspicious uncited claim(s) detected:\n"
                    f"{warning_lines}\n"
                    "ACTION REQUIRED: verify each flagged claim with bash() or web_search() and "
                    "rewrite with explicit citations before proceeding."
                )

        return result
    except Exception as e:
        return f"ERROR: {e}"


def tool_web_search(query: str, max_results: int = 5) -> str:
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"No results found for query: {query}"
        lines = [f"Search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', 'No title')}")
            lines.append(f"    URL: {r.get('href', '')}")
            lines.append(f"    {r.get('body', '')}")
            lines.append("")
        return "\n".join(lines)
    except ImportError:
        return "ERROR: duckduckgo_search not installed. Run: pip install duckduckgo_search"
    except Exception as e:
        return f"ERROR: web_search failed: {e}"


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


def make_tool_done(router):
    def tool_done(summary: str) -> str:
        # Gate 1: check evals/criteria.md for unchecked items
        criteria_path = Path("evals/criteria.md")
        if criteria_path.exists():
            lines = criteria_path.read_text(encoding="utf-8").splitlines()
            unchecked = [l.strip() for l in lines if l.strip().startswith("- [ ]")]
            if unchecked:
                items = "\n".join(f"  {u}" for u in unchecked)
                return (
                    f"REJECTED — {len(unchecked)} criterion/criteria not yet completed:\n{items}\n\n"
                    "Complete these, update evals/criteria.md (change '- [ ]' to '- [x]'), then call done() again."
                )

        # Gate 2: results/ must have output files
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        result_files = [f for f in results_dir.rglob("*") if f.is_file() and f.name != "SUMMARY.md"]
        if not result_files:
            return (
                "REJECTED — results/ directory is empty. "
                "You must produce at least one output file (CSV, plot, report) before calling done()."
            )

        # Gate 3: LLM judge — verify each criterion against actual outputs
        try:
            criteria_text = criteria_path.read_text(encoding="utf-8") if criteria_path.exists() else "(no criteria file)"
            results_contents = {}
            for f in result_files:
                try:
                    text = f.read_text(encoding="utf-8")
                    results_contents[str(f)] = text[:3000] + ("...[truncated]" if len(text) > 3000 else "")
                except Exception:
                    results_contents[str(f)] = "(binary or unreadable file)"

            results_block = "\n\n".join(
                f"--- {path} ---\n{content}" for path, content in results_contents.items()
            )[:8000]

            judge_prompt = f"""\
You are a strict research verifier. Your job is to check whether each success criterion has actually been satisfied by the outputs produced.

## Success Criteria (from evals/criteria.md)
{criteria_text}

## Result Files Produced
{results_block}

For every criterion marked [x], respond with exactly one line:
PASS: <criterion text> — <specific evidence from the result files>
FAIL: <criterion text> — <what is missing, wrong, or unverifiable>

Be strict. If the evidence is absent, vague, or the file is empty/malformed, mark FAIL.
Do not output anything other than PASS:/FAIL: lines."""

            print("  [harness] Running judge verification...")
            response = router.chat(
                [{"role": "user", "content": judge_prompt}],
                max_tokens=2000,
            )
            verdict = response.choices[0].message.content or ""
            failures = [l.strip() for l in verdict.splitlines() if l.strip().startswith("FAIL:")]
            passes = [l.strip() for l in verdict.splitlines() if l.strip().startswith("PASS:")]
            print(f"  [harness] Judge: {len(passes)} pass, {len(failures)} fail")

            if failures:
                failure_list = "\n".join(f"  {f}" for f in failures)
                return (
                    f"REJECTED — Judge verification failed on {len(failures)} criterion/criteria:\n"
                    f"{failure_list}\n\n"
                    "Fix these issues, then call done() again."
                )

        except Exception as e:
            print(f"  [harness] Judge error (failing open): {e}")
            # Fail open — don't block completion if judge itself errors

        summary_path = results_dir / "SUMMARY.md"
        summary_path.write_text(f"# Research Summary\n\n{summary}\n", encoding="utf-8")
        return "ACCEPTED — Research complete. Summary saved to results/SUMMARY.md"

    return tool_done


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

def build_tool_dispatch(router) -> dict:
    return {
        "bash": tool_bash,
        "write_file": tool_write_file,
        "read_file": tool_read_file,
        "list_files": tool_list_files,
        "web_search": tool_web_search,
        "git_commit": tool_git_commit,
        "done": make_tool_done(router),
    }


def execute_tool(name: str, args: dict, dispatch: dict) -> str:
    fn = dispatch.get(name)
    if not fn:
        return f"ERROR: Unknown tool: {name}"
    try:
        return fn(**args)
    except Exception as e:
        return f"ERROR executing {name}: {e}"


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context(round_num: int = 0, phase: str = "work") -> str:
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

        # Pre-flight hallucination scan
        preflight_warnings = check_for_hallucinations(journal_content)
        if preflight_warnings:
            warning_lines = "\n".join(f"  - {w}" for w in preflight_warnings[:10])
            journal_preflight = (
                f"⚠️  PRE-FLIGHT WARNING — {len(preflight_warnings)} potentially uncited claim(s) "
                f"in journal from previous rounds:\n{warning_lines}\n"
                "Treat these as HYPOTHESES until re-verified with bash() or web_search() this round.\n\n"
            )
        else:
            journal_preflight = ""

        # Per-round verify-first instruction (work mode, not the first round)
        if round_num > 0 and phase == "work":
            verify_first = (
                "⚡ VERIFY FIRST — before doing new work this round:\n"
                "Re-run the key bash()/web_search() commands from the last round to confirm "
                "outputs are still valid. If anything changed or failed, fix it before proceeding.\n\n"
            )
        else:
            verify_first = ""
    else:
        journal_content = "(empty — this is round 1)"
        journal_preflight = ""
        verify_first = ""

    return f"""\
## PROGRAM (your goal)
{program}

## SUCCESS CRITERIA
{criteria}

## JOURNAL (your progress log)
{verify_first}{journal_preflight}{journal_content}
"""


# ---------------------------------------------------------------------------
# State persistence (for --continue)
# ---------------------------------------------------------------------------

STATE_FILE = ".harness_state.json"


def save_state(round_num: int, phase: str, verify_rounds_remaining: int,
               commits_since_push: int, last_push_time: float):
    state = {
        "round_num": round_num,
        "phase": phase,
        "verify_rounds_remaining": verify_rounds_remaining,
        "commits_since_push": commits_since_push,
        "last_push_time": last_push_time,
    }
    Path(STATE_FILE).write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_state() -> dict | None:
    p = Path(STATE_FILE)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [harness] WARNING: Could not load state file: {e}")
    return None


def clear_state():
    p = Path(STATE_FILE)
    if p.exists():
        p.unlink()


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
    if not response.choices:
        print("  [harness] Empty choices in response — skipping")
        return [], {"role": "assistant", "content": ""}
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

def git_push():
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  [harness] git push OK")
    else:
        print(f"  [harness] git push failed: {result.stderr.strip()}")


def run_research(config_path=None, max_rounds=None, max_tool_calls_per_round=None, continue_run=False):
    if not Path("program.md").exists():
        print("ERROR: program.md not found. Create it first.")
        sys.exit(1)

    ensure_git_configured()
    router = LLMRouter(config_path=config_path)
    dispatch = build_tool_dispatch(router)

    # Load limits from config or use defaults
    cfg = router._config
    effective_max_rounds = max_rounds or cfg.get("max_rounds", 20)
    effective_max_tools = max_tool_calls_per_round or cfg.get("max_tool_calls_per_round", 50)
    push_every_n_commits = cfg.get("push_every_n_commits", 5)
    push_every_minutes = cfg.get("push_every_minutes", 15)
    verification_rounds = cfg.get("verification_rounds", 1)

    # Default initial state
    start_round = 0
    commits_since_push = 0
    last_push_time = time.time()
    phase = "work"                   # "work" | "verify"
    verify_rounds_remaining = verification_rounds

    if continue_run:
        state = load_state()
        if state:
            start_round = state.get("round_num", 0)
            phase = state.get("phase", "work")
            verify_rounds_remaining = state.get("verify_rounds_remaining", verification_rounds)
            commits_since_push = state.get("commits_since_push", 0)
            last_push_time = state.get("last_push_time", time.time())
            print(f"[harness] Resuming from round {start_round + 1}, phase={phase}")
        else:
            print("[harness] --continue specified but no state file found — starting fresh")

    print(f"Starting research: max_rounds={effective_max_rounds}, max_tool_calls={effective_max_tools}")
    print(f"Auto-push: every {push_every_n_commits} commits or {push_every_minutes} min")
    print(f"Verification rounds after done(): {verification_rounds}")

    for round_num in range(start_round, effective_max_rounds):
        print(f"\n{'='*60}")
        print(f"=== Round {round_num + 1} / {effective_max_rounds}  [{phase.upper()}] ===")
        print(f"{'='*60}")

        # Persist state so --continue can resume from this round if killed
        save_state(round_num, phase, verify_rounds_remaining, commits_since_push, last_push_time)

        system_prompt = VERIFICATION_PROMPT if phase == "verify" else SYSTEM_PROMPT
        context = build_context(round_num=round_num, phase=phase)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context},
        ]

        round_done = False
        truly_done = False
        nudge_count = 0

        for tool_call_num in range(effective_max_tools):
            try:
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

                nudge_count = 0

                for tc in tool_calls:
                    result = execute_tool(tc["name"], tc["args"], dispatch)
                    preview = result[:120].replace("\n", " ")
                    print(f"  [{tc['name']}] → {preview}")
                    messages.append(make_tool_result_message(tc["id"], result))

                    if tc["name"] == "git_commit":
                        round_done = True
                        # git_commit in verify mode means issues found — back to work
                        if phase == "verify":
                            print("  [harness] Verify round found issues — switching back to work mode")
                            phase = "work"
                            verify_rounds_remaining = verification_rounds
                        commits_since_push += 1
                        elapsed_min = (time.time() - last_push_time) / 60
                        if commits_since_push >= push_every_n_commits or elapsed_min >= push_every_minutes:
                            git_push()
                            commits_since_push = 0
                            last_push_time = time.time()

                    if tc["name"] == "done" and result.startswith("ACCEPTED"):
                        if phase == "work" and verify_rounds_remaining > 0:
                            # Transition to verification mode
                            verify_rounds_remaining -= 1
                            phase = "verify"
                            round_done = True
                            print(f"  [harness] Work accepted — entering verification mode "
                                  f"({verify_rounds_remaining + 1} round(s) remaining)")
                        else:
                            # Verification passed (or no verify rounds configured)
                            truly_done = True

            except Exception as e:
                print(f"  [harness] Unexpected error (continuing): {type(e).__name__}: {e}")
                continue

            if round_done or truly_done:
                break

        if truly_done:
            print("\n[harness] Research complete and verified! Auto-committing and pushing...")
            subprocess.run(["git", "add", "-A"])
            subprocess.run([
                "git", "commit",
                "--author=autoresearch <agent@autoresearch.local>",
                "-m", "auto-commit: research complete", "--allow-empty"
            ])
            git_push()
            clear_state()
            print("[harness] Done.")
            return

    print(f"\n[harness] Reached max rounds ({effective_max_rounds}). Research loop ended.")
    print(f"[harness] State saved — resume with --continue")


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
    parser.add_argument("--continue", dest="continue_run", action="store_true",
                        help="Resume a previously interrupted run from saved state")
    args = parser.parse_args()

    # Resolve config path before any chdir, so relative paths still work
    config_path = args.config
    if not config_path:
        for candidate in [Path.home() / ".llm_router_config.json", Path("llm_router_config.json")]:
            if candidate.exists():
                config_path = str(candidate.resolve())
                break

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
        config_path=config_path,
        max_rounds=args.max_rounds,
        max_tool_calls_per_round=args.max_tool_calls,
        continue_run=args.continue_run,
    )


if __name__ == "__main__":
    main()
