# MiroFish CLI AGY (`mirofish-cli-agy`)

MiroFish is a universal multi-agent prediction sandbox and social simulation engine.
It digests input seed documents, builds a knowledge graph (GraphRAG), initializes autonomous persona agents, and runs interactive simulation loops on simulated Twitter and Reddit environments.

## Core Provider

- Default Provider: `agy-cli` (powered by Google Antigravity CLI via `agy -p prompt --output-format json`).
- Supported Alternatives: `claude-cli` (Anthropic Claude Code CLI), `codex-cli` (OpenAI Codex CLI).

## Execution Commands

- Run simulation: `mirofish run --files <file1> <file2> --requirement "<prediction query>" --max-rounds <N>`
- Diagnostics: `mirofish doctor`
- List runs: `mirofish runs list --json`
- Inspect run: `mirofish runs status <run_id> --json`
- Export run: `mirofish runs export <run_id> --json`
