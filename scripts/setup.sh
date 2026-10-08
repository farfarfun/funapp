#!/bin/bash
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"
PORT=5678
PID_FILE="$RUN_DIR/funapp.pid"
LOG_FILE="$RUN_DIR/funapp.log"

usage() {
    echo "用法: $0 {install-dev|publish|start|stop|restart|run|status} | $0 install-prod [version]" >&2
    exit 1
}

process_started_at() {
    if [ -r "/proc/$1/stat" ]; then
        awk '{print $22}' "/proc/$1/stat"
    else
        ps -p "$1" -o lstart= 2>/dev/null | xargs
    fi
}

is_running() {
    local pid started_at actual_started_at
    [ -f "$PID_FILE" ] || return 1
    read -r pid started_at < "$PID_FILE"
    if [[ "$pid" =~ ^[1-9][0-9]*$ ]] && [ -n "$started_at" ] \
        && kill -0 "$pid" 2>/dev/null; then
        actual_started_at=$(process_started_at "$pid")
        if [ "$actual_started_at" = "$started_at" ]; then
            return 0
        fi
    fi
    if [ -n "${pid:-}" ]; then
        echo "funapp 发现陈旧 PID 文件，已清理 (pid $pid)" >&2
    else
        echo "funapp 发现无效 PID 文件，已清理" >&2
    fi
    rm -f "$PID_FILE"
    return 1
}

installed_cli() {
    command -v funapp 2>/dev/null || {
        echo "error: 未安装 funapp，请先执行 install-dev 或 install-prod" >&2
        exit 1
    }
}

installed_version() {
    python3 -c 'from importlib.metadata import version; print(version("funapp"))' 2>/dev/null || echo "未安装"
}

start_cmd() {
    local cli
    cli=$(installed_cli)
    mkdir -p "$RUN_DIR"
    cd "$RUN_DIR"
    unset PYTHONPATH
    exec "$cli"
}

do_start() {
    mkdir -p "$RUN_DIR"
    if is_running; then
        echo "funapp 已在运行 (pid $(cut -d ' ' -f 1 "$PID_FILE"))" >&2
        exit 1
    fi
    installed_cli >/dev/null
    nohup "$0" run >"$LOG_FILE" 2>&1 &
    local pid=$!
    local started_at
    started_at=$(process_started_at "$pid")
    if [ -z "$started_at" ]; then
        echo "funapp 无法读取启动进程信息" >&2
        return 1
    fi
    printf '%s %s\n' "$pid" "$started_at" > "$PID_FILE"
    echo "funapp 已在后台启动 (version $(installed_version), pid $pid, port $PORT)"
}

do_stop() {
    if ! is_running; then
        echo "funapp 未在运行" >&2
        return
    fi
    local pid
    read -r pid _ < "$PID_FILE"
    kill "$pid"
    rm -f "$PID_FILE"
    echo "funapp 已停止"
}

do_run() {
    start_cmd
}

do_status() {
    local version
    version=$(installed_version)
    if is_running; then
        local pid
        read -r pid _ < "$PID_FILE"
        echo "funapp $version 运行中 (pid $pid, port $PORT)"
    else
        echo "funapp $version 未运行"
    fi
}

require_funbuild() {
    command -v funbuild >/dev/null 2>&1 || {
        echo "error: 需要先安装 funbuild" >&2
        exit 1
    }
}

action="${1:-}"
case "$action" in
    start|stop|restart|run|status|install-dev|publish)
        [ "$#" -eq 1 ] || usage
        ;;
    install-prod)
        [ "$#" -le 2 ] || usage
        ;;
    *)
        usage
        ;;
esac

case "$action" in
    start) do_start ;;
    stop) do_stop ;;
    restart)
        do_stop || true
        do_start
        ;;
    run) do_run ;;
    status) do_status ;;
    install-dev)
        require_funbuild
        (cd "$ROOT_DIR" && funbuild install)
        ;;
    install-prod)
        python3 -m pip install "funapp${2:+==$2}"
        ;;
    publish)
        require_funbuild
        (cd "$ROOT_DIR" && funbuild build)
        ;;
esac
