#!/usr/bin/env bash
# kramlipi code-agent — one-script Chat UI
#
# Setup (that's it):
#   export GEMINI_API_KEY=your-key    # or OPENAI_API_KEY / ANTHROPIC_API_KEY
#   bash docker-ui.sh
#   → http://127.0.0.1:8080
#
# Paste this file anywhere. No repo clone required.
# Optional: WORKSPACE=… PORT=8080 IMAGE=… HOST_ROOT=… PULL=0
set -euo pipefail

IMAGE="${IMAGE:-ghcr.io/kramlipi/code-agent:latest}"
HOST_ROOT="${HOST_ROOT:-${HOME:-/tmp}}"
HOST_ROOT="$(cd "$HOST_ROOT" && pwd)"
WORKSPACE="${WORKSPACE:-${WORKSPACE_PATH:-$PWD}}"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"
PORT="${PORT:-8080}"
PULL="${PULL:-1}"

HOST_ENV_VARS=(
  GEMINI_API_KEY GOOGLE_API_KEY OPENAI_API_KEY ANTHROPIC_API_KEY
  DEEPSEEK_API_KEY CODE_AGENT_MODEL CODE_AGENT_API_BASE CODE_AGENT_API_KEY
  CODE_AGENT_LOG_LEVEL GH_TOKEN GITHUB_TOKEN
)

echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│  kramlipi code-agent                        │"
echo "│  1. pull image                              │"
echo "│  2. run this script                         │"
echo "│  3. open http://127.0.0.1:${PORT}              │"
echo "└─────────────────────────────────────────────┘"
echo ""
echo "  Image      $IMAGE"
echo "  Browse     $HOST_ROOT"
echo "  Workspace  $WORKSPACE"
echo ""

# --- 1. Pull ---
if [ "$PULL" = "1" ] || [ "$PULL" = "true" ]; then
  if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "✓ Image ready (cached)"
  else
    echo "↓ Pulling $IMAGE ..."
    if ! docker pull "$IMAGE"; then
      echo ""
      echo "Pull failed. If the package is private:"
      echo "  echo \"\$GITHUB_TOKEN\" | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin"
      exit 1
    fi
    echo "✓ Image pulled"
  fi
else
  echo "· Skipping pull (PULL=0)"
fi

# --- 2. Host API keys ---
DOCKER_HOST_ENV_ARGS=(
  -e "HOME=${HOME:-$HOST_ROOT}"
  -e "CODE_AGENT_HOST_HOME=${HOME:-$HOST_ROOT}"
  -e "CODE_AGENT_HOST_ROOT=$HOST_ROOT"
  -e "CODE_AGENT_WORKSPACE=$WORKSPACE"
)
found=()
for name in "${HOST_ENV_VARS[@]}"; do
  if [ -n "${!name:-}" ]; then
    DOCKER_HOST_ENV_ARGS+=(-e "$name")
    found+=("$name")
  fi
done
if [ "${#found[@]}" -eq 0 ]; then
  echo "! No API key in host env — set GEMINI_API_KEY (or OPENAI_API_KEY) then re-run"
else
  echo "✓ Host keys: ${found[*]}"
fi

ENV_FILE_ARGS=()
# If script lives in a git checkout, pick up repo .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
for candidate in "$PWD/.env" "$SCRIPT_DIR/.env" "$SCRIPT_DIR/../.env"; do
  if [ -f "$candidate" ]; then
    ENV_FILE_ARGS=(--env-file "$candidate")
    echo "✓ env-file  $candidate"
    break
  fi
done

VOLUME_ARGS=(-v "${HOST_ROOT}:${HOST_ROOT}")
case "$WORKSPACE" in
  "$HOST_ROOT"|"$HOST_ROOT"/*) ;;
  *) VOLUME_ARGS+=(-v "${WORKSPACE}:${WORKSPACE}") ;;
esac

USER_ARGS=()
if [ "$(id -u)" -ne 0 ]; then
  USER_ARGS=(--user "$(id -u):$(id -g)")
fi

DOCKER_TTY=(--rm)
if [ -t 0 ] && [ -t 1 ]; then
  DOCKER_TTY+=(-it)
else
  DOCKER_TTY+=(-i)
fi

echo ""
echo "→ Ready. Chat UI → http://127.0.0.1:${PORT}"
echo "  Open folder → pick a project → ask it to fix unit tests."
echo ""

# --- 3. Launch ---
exec docker run "${DOCKER_TTY[@]}" \
  "${USER_ARGS[@]}" \
  "${ENV_FILE_ARGS[@]}" \
  "${DOCKER_HOST_ENV_ARGS[@]}" \
  -p "${PORT}:8080" \
  "${VOLUME_ARGS[@]}" \
  -w "$WORKSPACE" \
  "$IMAGE" \
  web serve --host 0.0.0.0 --port 8080 -w "$WORKSPACE"
