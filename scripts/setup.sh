#!/bin/bash
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"
PID_FILE="$RUN_DIR/funapp.pid"
LOG_FILE="$RUN_DIR/funapp.log"
PORT=5678

usage() {
    echo "用法: $0 {start|stop|restart|run|status} {dev|prod}" >&2
    exit 1
}

is_running() {
    [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

start_cmd() {
    local env="$1"
    if [ "$env" = "prod" ]; then
        python3 -c "from funapp.server.core import run; run()"
    else
        (cd "$ROOT_DIR" && python3 -c "from funapp.server.core import run; run()")
    fi
}

do_start() {
    local env="$1"
    mkdir -p "$RUN_DIR"
    if is_running; then
        echo "funapp 已在运行 (pid $(cat "$PID_FILE"))" >&2
        exit 1
    fi
    nohup bash -c "$(declare -f start_cmd); start_cmd '$env'" >"$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "funapp 已在后台启动 (env=$env, pid $(cat "$PID_FILE"), port $PORT)"
}

do_stop() {
    if ! is_running; then
        echo "funapp 未在运行" >&2
        rm -f "$PID_FILE"
        return
    fi
    kill "$(cat "$PID_FILE")"
    rm -f "$PID_FILE"
    echo "funapp 已停止"
}

do_run() {
    local env="$1"
    mkdir -p "$RUN_DIR"
    start_cmd "$env"
}

do_status() {
    if is_running; then
        echo "funapp 运行中 (pid $(cat "$PID_FILE"), port $PORT)"
    else
        echo "funapp 未运行"
    fi
}

action="${1:-}"
env="${2:-}"

case "$action" in
    start|stop|restart|run)
        [ "$env" = "dev" ] || [ "$env" = "prod" ] || usage
        ;;
esac

case "$action" in
    start)
        do_start "$env"
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_stop || true
        do_start "$env"
        ;;
    run)
        do_run "$env"
        ;;
    status)
        do_status
        ;;
    *)
        usage
        ;;
esac
