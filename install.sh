#!/usr/bin/env bash
set -e

# MiroFish CLI AGY - One-Line Universal Installer

INSTALL_DIR="${HOME}/.mirofish-cli-agy"
TARGET_DIR="$(pwd)"

# If current directory is the repo, use it. Otherwise, clone or update INSTALL_DIR.
if [ -f "${TARGET_DIR}/pyproject.toml" ] && grep -q "mirofish-cli-agy" "${TARGET_DIR}/pyproject.toml" 2>/dev/null; then
    REPO_DIR="${TARGET_DIR}"
else
    REPO_DIR="${INSTALL_DIR}"
    if [ ! -d "${REPO_DIR}" ]; then
        echo "Cloning mirofish-cli-agy into ${REPO_DIR}..."
        git clone https://github.com/almazid-shisir/mirofish-cli-agy.git "${REPO_DIR}"
    else
        echo "Updating existing installation in ${REPO_DIR}..."
        cd "${REPO_DIR}" && git pull origin main || true
    fi
fi

cd "${REPO_DIR}"

# Ensure ~/.local/bin is in PATH
export PATH="${HOME}/.local/bin:${PATH}"

# Check or install uv
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.cargo/bin:${PATH}"
fi

# Install dependencies and CLI tool
echo "Installing MiroFish dependencies and CLI binaries..."
uv sync
uv tool install --editable . --force || true

# Auto-detect available agent CLIs
AGY_FOUND=false
CLAUDE_FOUND=false
CODEX_FOUND=false

command -v agy >/dev/null 2>&1 && AGY_FOUND=true
command -v claude >/dev/null 2>&1 && CLAUDE_FOUND=true
command -v codex >/dev/null 2>&1 && CODEX_FOUND=true

echo ""
echo "=========================================="
echo " Detected Agent Engines on System:"
echo "=========================================="
if [ "$AGY_FOUND" = true ]; then
    echo " [1] Google Antigravity CLI (agy) - INSTALLED"
else
    echo " [1] Google Antigravity CLI (agy) - Not found"
fi

if [ "$CLAUDE_FOUND" = true ]; then
    echo " [2] Anthropic Claude Code CLI (claude) - INSTALLED"
else
    echo " [2] Anthropic Claude Code CLI (claude) - Not found"
fi

if [ "$CODEX_FOUND" = true ]; then
    echo " [3] OpenAI Codex CLI (codex) - INSTALLED"
else
    echo " [3] OpenAI Codex CLI (codex) - Not found"
fi
echo "=========================================="

# Select Agent Provider
SELECTED_PROVIDER="agy-cli"

# Try reading from terminal if available
INPUT_SRC=""
if [ -t 0 ]; then
    INPUT_SRC="/dev/stdin"
elif [ -c /dev/tty ]; then
    INPUT_SRC="/dev/tty"
fi

if [ -n "$INPUT_SRC" ]; then
    echo -n "Select Agent Engine [1, 2, or 3] (Default: 1): "
    read -r CHOICE < "$INPUT_SRC" || CHOICE="1"
    case "$CHOICE" in
        2) SELECTED_PROVIDER="claude-cli" ;;
        3) SELECTED_PROVIDER="codex-cli" ;;
        *) SELECTED_PROVIDER="agy-cli" ;;
    esac
else
    # Auto-detect fallback
    if [ "$AGY_FOUND" = true ]; then
        SELECTED_PROVIDER="agy-cli"
    elif [ "$CLAUDE_FOUND" = true ]; then
        SELECTED_PROVIDER="claude-cli"
    elif [ "$CODEX_FOUND" = true ]; then
        SELECTED_PROVIDER="codex-cli"
    fi
fi

echo "Selected Provider: ${SELECTED_PROVIDER}"

# Configure .env
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Update LLM_PROVIDER in .env
sed -i "s/^LLM_PROVIDER=.*/LLM_PROVIDER=${SELECTED_PROVIDER}/" .env

# Register MCP server with Antigravity CLI if agy is present
if [ "$AGY_FOUND" = true ]; then
    echo "Registering MiroFish MCP server with Antigravity CLI..."
    agy mcp add mirofish "${HOME}/.local/bin/mirofish-mcp" 2>/dev/null || true
fi

# Run diagnostics
echo ""
echo "Running system diagnostics..."
"${HOME}/.local/bin/mirofish" doctor || uv run python -m app.cli doctor

echo ""
echo "============================================================"
echo " Installation Complete!"
echo " Provider Configured: ${SELECTED_PROVIDER}"
echo " CLI Command: mirofish --help"
echo " MCP Server:  ${HOME}/.local/bin/mirofish-mcp"
echo "============================================================"
