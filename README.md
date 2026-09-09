# Agent Module

This repository is a small apprenticeship project for building and testing a tool-using coding agent. It contains a single Python entrypoint that talks to the Anthropic API, exposes a narrow set of local tools, and runs a turn-based agent loop that can read files, write files, and execute shell commands with explicit user approval.

The repo also includes a tiny sample project used as a safe target for experiments. That sample project is a basic calculator module with pytest tests, which makes it useful for validating agent behaviors such as reading code, making edits, and running tests.

## What Is In The Repo

- `agent.py`: the minimal agent implementation.
- `sample_project/`: a toy Python project the agent can inspect and modify.
- `sample_project/test_calculator.py`: a small test suite for verification workflows.

## How It Works

The agent sends your prompt to Anthropic, receives either normal text or tool calls, executes approved tool calls locally, and feeds the results back into the conversation until the model ends its turn. The available tools are intentionally small in scope:

- `read_file` to inspect files or list directory contents.
- `write_file` to overwrite file contents.
- `run_shell` to run commands such as tests or git checks, gated by a confirmation prompt.

## Running The Agent

Export your Anthropic API key in the current shell session and then start the agent:

```bash
export ANTHROPIC_API_KEY="..."

pipenv run python agent.py "your prompt here"
```

## Example Uses

- Ask the agent to summarize a module.
- Ask it to add documentation to a file.
- Ask it to run the sample tests and diagnose failures.
- Ask it to edit the sample calculator code and verify the result.

## Purpose

This repo is best understood as a minimal sandbox for learning agent orchestration: prompt in, tool calls out, local execution, and iterative reasoning over file and command results. It is intentionally small enough to inspect end-to-end, while still being realistic enough to practice debugging and agent-assisted code changes.
