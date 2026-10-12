#!/usr/bin/env bash
# ==============================================================================
# Smart Farming All-in-One Service Launcher (Pop!_OS / Linux)
# Starts Backend API (8000), Model Inference Server (8001), Frontend UI (5173),
# and ARQ Redis Worker with unified logging and auto-restart watchdog.
# ==============================================================================

set -euo pipefail

# ANSI color codes
CYAN='\033[1;36m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
MAGENTA='\033[1;35m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

SEPARATE_WINDOWS=false
INCLUDE_MOBILE=false

show_help() {
    cat << EOF
Usage: ./start_all.sh [OPTIONS]

Options:
  -s, --separate-windows, --windows   Launch each service in a separate terminal window
  -m, --mobile, -IncludeMobile        Launch Flutter mobile web app alongside backend & frontend
  -h, --help                          Show this help message
EOF
    exit 0
}

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--separate-windows|--windows|-windowed)
            SEPARATE_WINDOWS=true
            shift
            ;;
        -m|--mobile|-IncludeMobile)
            INCLUDE_MOBILE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
MODEL_DIR="$ROOT_DIR/model_service"
MOBILE_DIR="$ROOT_DIR/mobile"

# Locate uvicorn for Backend
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/uvicorn" ]; then
    UVICORN_BIN="$VIRTUAL_ENV/bin/uvicorn"
elif [ -x "$BACKEND_DIR/.venv/bin/uvicorn" ]; then
    UVICORN_BIN="$BACKEND_DIR/.venv/bin/uvicorn"
elif [ -x "$HOME/.venvs/smart-farming-backend/bin/uvicorn" ]; then
    UVICORN_BIN="$HOME/.venvs/smart-farming-backend/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
    UVICORN_BIN="uvicorn"
else
    UVICORN_BIN="python3 -m uvicorn"
fi

# Locate uvicorn for Model Service
if [ -x "$MODEL_DIR/.venv/bin/uvicorn" ]; then
    MODEL_UVICORN_BIN="$MODEL_DIR/.venv/bin/uvicorn"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/uvicorn" ]; then
    MODEL_UVICORN_BIN="$VIRTUAL_ENV/bin/uvicorn"
else
    MODEL_UVICORN_BIN="$UVICORN_BIN"
fi

# Locate ARQ binary
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/arq" ]; then
    ARQ_BIN="$VIRTUAL_ENV/bin/arq"
elif [ -x "$BACKEND_DIR/.venv/bin/arq" ]; then
    ARQ_BIN="$BACKEND_DIR/.venv/bin/arq"
elif [ -x "$HOME/.venvs/smart-farming-backend/bin/arq" ]; then
    ARQ_BIN="$HOME/.venvs/smart-farming-backend/bin/arq"
elif command -v arq >/dev/null 2>&1; then
    ARQ_BIN="arq"
else
    ARQ_BIN="python3 -m arq"
fi

echo ""
echo -e "${CYAN}========================================================${NC}"
echo -e "${CYAN}              SMART FARMING - STARTING${NC}"
echo -e "${CYAN}========================================================${NC}"
echo ""
echo -e "${GRAY}[SYSTEM] Project Root: ${NC}$ROOT_DIR"
if [ "$INCLUDE_MOBILE" = true ]; then
    echo -e "${GRAY}[SYSTEM] Mobile Mode:  ${CYAN}Enabled (Chrome device target)${NC}"
fi
echo ""

# Function to detect installed terminal emulator for separate windows mode
detect_terminal() {
    if command -v cosmic-term >/dev/null 2>&1; then
        echo "cosmic-term"
    elif command -v x-terminal-emulator >/dev/null 2>&1; then
        echo "x-terminal-emulator"
    elif command -v gnome-terminal >/dev/null 2>&1; then
        echo "gnome-terminal"
    elif command -v alacritty >/dev/null 2>&1; then
        echo "alacritty"
    elif command -v kitty >/dev/null 2>&1; then
        echo "kitty"
    elif command -v konsole >/dev/null 2>&1; then
        echo "konsole"
    elif command -v xterm >/dev/null 2>&1; then
        echo "xterm"
    else
        echo ""
    fi
}

launch_in_term() {
    local title="$1"
    local work_dir="$2"
    local cmd="$3"
    local term="$4"

    case "$term" in
        cosmic-term)
            cosmic-term -w "$work_dir" -e bash -c "echo -ne \"\033]0;$title\007\"; $cmd; exec bash" &
            ;;
        x-terminal-emulator|gnome-terminal)
            "$term" --title="$title" --working-directory="$work_dir" -- bash -c "$cmd; exec bash" &
            ;;
        konsole)
            konsole --new-tab -p tabtitle="$title" --workdir "$work_dir" -e bash -c "$cmd; exec bash" &
            ;;
        alacritty)
            alacritty --title "$title" --working-directory "$work_dir" -e bash -c "$cmd; exec bash" &
            ;;
        kitty)
            kitty --title "$title" --directory "$work_dir" bash -c "$cmd; exec bash" &
            ;;
        xterm)
            xterm -title "$title" -e bash -c "cd '$work_dir' && $cmd; exec bash" &
            ;;
        *)
            echo -e "${RED}Unsupported terminal: $term${NC}"
            ;;
    esac
}

# --- Separate Windows Mode ---
if [ "$SEPARATE_WINDOWS" = true ]; then
    TERM_EMULATOR="$(detect_terminal)"
    if [ -z "$TERM_EMULATOR" ] || { [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; }; then
        echo -e "${YELLOW}[MODE] No graphical display / terminal emulator detected. Falling back to unified streaming mode...${NC}"
        SEPARATE_WINDOWS=false
    else
        echo -e "${YELLOW}[MODE] Launching services in separate terminal windows using $TERM_EMULATOR...${NC}"
        echo ""

        echo -e "${GREEN}[1/4] Starting Server 1: Backend API (Port 8000)...${NC}"
        launch_in_term "Smart Farming - Backend API" "$BACKEND_DIR" "$UVICORN_BIN src.app.main:app --host 127.0.0.1 --port 8000 --reload" "$TERM_EMULATOR"

        echo -e "${BLUE}[2/4] Starting Server 2: Model Inference Server (Port 8001)...${NC}"
        launch_in_term "Smart Farming - Model Inference Server" "$MODEL_DIR" "$MODEL_UVICORN_BIN main:app --host 127.0.0.1 --port 8001 --reload" "$TERM_EMULATOR"

        echo -e "${MAGENTA}[3/4] Starting Server 3: Frontend (Port 5173)...${NC}"
        launch_in_term "Smart Farming - Frontend UI" "$FRONTEND_DIR" "npm run dev" "$TERM_EMULATOR"

        echo -e "${YELLOW}[4/4] Starting Server 4: ARQ Worker (Redis Queue)...${NC}"
        launch_in_term "Smart Farming - ARQ Worker" "$BACKEND_DIR" "export PYTHONIOENCODING=utf-8 && $ARQ_BIN src.app.worker.WorkerSettings" "$TERM_EMULATOR"

        if [ "$INCLUDE_MOBILE" = true ]; then
            echo -e "${CYAN}[5/5] Starting Server 5: Mobile App (Flutter in Chrome)...${NC}"
            launch_in_term "Smart Farming - Mobile App" "$MOBILE_DIR" "flutter run -d chrome" "$TERM_EMULATOR"
        fi

        echo ""
        echo -e "${CYAN}========================================================${NC}"
        echo -e "${CYAN}              ALL SERVICES LAUNCHED${NC}"
        echo -e "${CYAN}========================================================${NC}"
        echo ""
        echo -e "  BACKEND   -> ${GREEN}http://127.0.0.1:8000${NC}"
        echo -e "  MODEL     -> ${BLUE}http://127.0.0.1:8001${NC}"
        echo -e "  FRONTEND  -> ${MAGENTA}http://localhost:5173${NC}"
        echo -e "  ARQ       -> ${YELLOW}Redis background worker${NC}"
        if [ "$INCLUDE_MOBILE" = true ]; then
            echo -e "  MOBILE    -> ${CYAN}Flutter Web (Chrome)${NC}"
        fi
        echo ""
        echo -e "${GRAY}Each service is running in its own titled window.${NC}"
        exit 0
    fi
fi

# --- Unified Streaming Mode ---
STOPPING=false
declare -A SERVICE_PIDS

kill_process_tree() {
    local parent_pid=$1
    local children
    children=$(pgrep -P "$parent_pid" 2>/dev/null || true)
    for child in $children; do
        kill_process_tree "$child"
    done
    kill -TERM "$parent_pid" 2>/dev/null || true
}

cleanup() {
    if [ "$STOPPING" = true ]; then
        return
    fi
    STOPPING=true
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    for name in "${!SERVICE_PIDS[@]}"; do
        local pid="${SERVICE_PIDS[$name]}"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo -e "${GRAY}Killing $name (PID $pid)...${NC}"
            kill_process_tree "$pid"
        fi
    done

    # Give processes a moment to terminate gracefully, then force kill if needed
    sleep 1
    for name in "${!SERVICE_PIDS[@]}"; do
        local pid="${SERVICE_PIDS[$name]}"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    done

    # Release ports if still bound
    if command -v fuser >/dev/null 2>&1; then
        fuser -k 8000/tcp 2>/dev/null || true
        fuser -k 8001/tcp 2>/dev/null || true
        fuser -k 5173/tcp 2>/dev/null || true
    fi

    echo -e "${GREEN}All services stopped cleanly.${NC}"
    exit 0
}

trap cleanup INT TERM EXIT

start_service_process() {
    local name="$1"
    local dir="$2"
    local color="$3"
    shift 3
    local cmd=("$@")

    echo -e "${color}[$name] Starting...${NC}"

    (
        cd "$dir"
        exec "${cmd[@]}"
    ) 2>&1 | sed -u "s/^/$(printf "${color}[%-8s]${NC} " "$name")/" &

    local pid=$!
    SERVICE_PIDS["$name"]=$pid
}

# Start Backend
start_service_process "BACKEND" "$BACKEND_DIR" "$GREEN" $UVICORN_BIN src.app.main:app --host 127.0.0.1 --port 8000 --reload

# Start Model Inference Microservice
start_service_process "MODEL" "$MODEL_DIR" "$BLUE" $MODEL_UVICORN_BIN main:app --host 127.0.0.1 --port 8001 --reload

# Start Frontend Vite Dev Server
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${MAGENTA}[FRONTEND] Installing dependencies first...${NC}"
    (cd "$FRONTEND_DIR" && npm install)
fi
start_service_process "FRONTEND" "$FRONTEND_DIR" "$MAGENTA" npm run dev

# Start ARQ Worker
start_arq_worker() {
    export PYTHONIOENCODING="utf-8"
    start_service_process "ARQ" "$BACKEND_DIR" "$YELLOW" $ARQ_BIN src.app.worker.WorkerSettings
}
start_arq_worker

# Optional Mobile App
if [ "$INCLUDE_MOBILE" = true ]; then
    if command -v flutter >/dev/null 2>&1; then
        start_service_process "MOBILE" "$MOBILE_DIR" "$CYAN" flutter run -d chrome
    else
        echo -e "${RED}[MOBILE  ] Flutter command not found. Skipping mobile startup.${NC}"
    fi
fi

sleep 2

echo ""
echo -e "${CYAN}========================================================${NC}"
echo -e "${CYAN}              ALL SERVICES RUNNING${NC}"
echo -e "${CYAN}========================================================${NC}"
echo ""
echo -e "  BACKEND   -> ${GREEN}http://127.0.0.1:8000${NC}"
echo -e "  MODEL     -> ${BLUE}http://127.0.0.1:8001${NC}"
echo -e "  FRONTEND  -> ${MAGENTA}http://localhost:5173${NC}"
echo -e "  ARQ       -> ${YELLOW}Redis background worker${NC}"
if [ "$INCLUDE_MOBILE" = true ]; then
    echo -e "  MOBILE    -> ${CYAN}Flutter Web (Chrome)${NC}"
fi
echo ""
echo -e "${GRAY}Press Ctrl+C to stop all services cleanly.${NC}"
echo ""
echo -e "${CYAN}========================================================${NC}"
echo -e "${CYAN}                 LIVE LOGS${NC}"
echo -e "${CYAN}========================================================${NC}"
echo ""

# Watchdog loop
while [ "$STOPPING" = false ]; do
    # ARQ Auto-Restart Watchdog
    if [ -n "${SERVICE_PIDS["ARQ"]:-}" ]; then
        if ! kill -0 "${SERVICE_PIDS["ARQ"]}" 2>/dev/null; then
            if [ "$STOPPING" = false ]; then
                echo -e "${RED}[ARQ     ] PROCESS EXITED unexpectedly.${NC}"
                echo -e "${YELLOW}[ARQ     ] Automatically restarting worker in 3 seconds...${NC}"
                sleep 3
                if [ "$STOPPING" = false ]; then
                    start_arq_worker
                fi
            fi
        fi
    fi

    # Check if other critical services exited
    for name in "BACKEND" "MODEL" "FRONTEND"; do
        if [ -n "${SERVICE_PIDS[$name]:-}" ]; then
            if ! kill -0 "${SERVICE_PIDS[$name]}" 2>/dev/null; then
                if [ "$STOPPING" = false ]; then
                    echo -e "${RED}[$name] PROCESS EXITED.${NC}"
                    unset "SERVICE_PIDS[$name]"
                fi
            fi
        fi
    done

    sleep 1
done

