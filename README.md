# MiroFish CLI AGY (mirofish-cli-agy)

Universal Swarm Intelligence and Social Prediction Engine powered by Google Antigravity CLI (`agy`), Anthropic Claude Code (`claude`), OpenAI Codex (`codex`), and CAMEL-AI OASIS.

Feed seed documents into MiroFish to build a GraphRAG knowledge graph, generate autonomous persona agents, simulate social debates on Twitter/Reddit, and output quantitative predictions and reports. Zero extra API token costs.

---

## 1-Line Quick Install

Auto-detects system dependencies, discovers installed agent CLIs (`agy`, `claude`, `codex`), configures your provider, and registers the MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/almazid-shisir/mirofish-cli-agy/main/install.sh | bash
```

Manual install alternative:

```bash
git clone https://github.com/almazid-shisir/mirofish-cli-agy.git && cd mirofish-cli-agy
./install.sh
```

---

## Universal Agentic Prompt

Copy and paste this single prompt directly into **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **Codex (`codex`)**, or any **Agentic Orchestrator**:

```text
Run a predictive simulation using the MiroFish MCP server:
1. Verify system readiness with `mirofish_doctor`.
2. Start simulation with `mirofish_start_simulation`:
   - files: ["examples/test_scenario.md"]
   - requirement: "Predict public adoption, backlash risks, and 30-day sentiment trajectory"
   - max_rounds: 3
   - run_in_background: true
3. Check execution progress using `mirofish_get_status` until phase is 'completed'.
4. Fetch `mirofish_get_verdict` and `mirofish_get_report`.
5. Provide a briefing containing:
   - Prediction verdict and confidence score (0.0 to 1.0)
   - Core conflict dynamics and agent consensus
   - High-risk indicators and recommended actions
```

Direct CLI terminal execution alternative:

```bash
mirofish run --files examples/test_scenario.md --requirement "Predict public sentiment and adoption" --max-rounds 3 --json
```

---

## MCP Tools Reference

The built-in MCP server (`mirofish-mcp`) provides 8 tools:

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `mirofish_start_simulation` | `files`, `requirement`, `max_rounds`, `run_in_background` | Launch multi-agent prediction simulation |
| `mirofish_get_status` | `run_id` | Check execution progress and phase |
| `mirofish_list_runs` | None | List previous simulation runs |
| `mirofish_get_verdict` | `run_id` | Get quantitative prediction (`verdict.json`) |
| `mirofish_get_report` | `run_id` | Get full analytical report (`report.md`) |
| `mirofish_get_knowledge_graph` | `run_id` | Get GraphRAG nodes, entities, and edges |
| `mirofish_get_agents` | `run_id` | Get generated personas and debate logs |
| `mirofish_doctor` | None | Verify environment and CLI bridges |

---

## Output Files

Every run outputs to `uploads/runs/<run_id>/`:

```text
uploads/runs/<run_id>/
|-- manifest.json         # Run metadata, parameters, and timestamps
|-- report/
|   |-- verdict.json      # Structured prediction scores and risk signals
|   |-- summary.json      # Executive summary
|   `-- report.md         # In-depth markdown analytical report
|-- visuals/
|   `-- network.svg       # Social network interaction graph
`-- simulations/          # OASIS Twitter and Reddit conversation logs
```

---

## License

AGPL-3.0 License. Maintained by [almazid-shisir](https://github.com/almazid-shisir).
