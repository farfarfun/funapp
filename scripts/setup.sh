#!/bin/bash
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
RUN_DIR="$ROOT_DIR/.run"
PORT=5678

usage() {
    echo "用法: $0 {start|stop|restart|run} {dev|prod} | $0 status [dev|prod]" >&2
    exit 1
}

pid_file() { echo "$RUN_DIR/funapp-$1.pid"; }
log_file() { echo "$RUN_DIR/funapp-$1.log"; }

is_running() {
    local env="$1" pid_path pid
    pid_path=$(pid_file "$env")
    [ -f "$pid_path" ] || return 1
    pid=$(cat "$pid_path")
    if kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    echo "funapp[$env] 发现陈旧 PID 文件，已清理 (pid $pid)" >&2
    rm -f "$pid_path"
    return 1
}

check_prod_installed() {
    # prod 只能跑已安装的正式包，不能回退到本仓库源码；
    # 通过比对 funapp 包的实际加载路径是否落在本仓库目录内来判断。
    python3 - "$ROOT_DIR" <<'PYEOF'
import os
import sys

root_dir = os.path.realpath(sys.argv[1])
try:
    import funapp
except ImportError:
    print("error: 未安装 funapp 正式包，请先 pip install funapp（或 uv pip install funapp）", file=sys.stderr)
    sys.exit(1)

pkg_path = os.path.realpath(funapp.__file__)
if pkg_path.startswith(root_dir + os.sep):
    print(
        "error: 当前 funapp 是从本仓库源码目录加载的（{}），".format(pkg_path)
        + "prod 模式禁止直接跑源码，请先安装正式发布包",
        file=sys.stderr,
    )
    sys.exit(1)
PYEOF
}

start_cmd() {
    local env="$1"
    local -a cmd
    if [ "$env" = "prod" ]; then
        check_prod_installed
        cmd=(python3 -c "from funapp.server.core import run; run()")
    else
        # dev 模式强制优先加载本仓库 src/ 下的源码，避免被系统/全局环境里
        # 恰好装着的其它 funapp 版本掩盖，保证跑的就是本地改动。
        cd "$ROOT_DIR"
        cmd=(env "PYTHONPATH=$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" python3 -c "from funapp.server.core import run; run()")
    fi
    exec "${cmd[@]}"
}

do_start() {
    local env="$1"
    local pid_path log_path
    pid_path=$(pid_file "$env")
    log_path=$(log_file "$env")
    mkdir -p "$RUN_DIR"
    if is_running "$env"; then
        echo "funapp[$env] 已在运行 (pid $(cat "$pid_path"))" >&2
        exit 1
    fi
    nohup "$0" run "$env" >"$log_path" 2>&1 &
    echo $! > "$pid_path"
    echo "funapp[$env] 已在后台启动 (pid $(cat "$pid_path"), port $PORT)"
}

do_stop() {
    local env="$1" pid_path
    pid_path=$(pid_file "$env")
    if ! is_running "$env"; then
        echo "funapp[$env] 未在运行" >&2
        return
    fi
    kill "$(cat "$pid_path")"
    rm -f "$pid_path"
    echo "funapp[$env] 已停止"
}

do_run() {
    local env="$1"
    mkdir -p "$RUN_DIR"
    start_cmd "$env"
}

do_status() {
    local env="$1" pid_path
    pid_path=$(pid_file "$env")
    if is_running "$env"; then
        echo "funapp[$env] 运行中 (pid $(cat "$pid_path"), port $PORT)"
    else
        echo "funapp[$env] 未运行"
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
        [ -z "$env" ] || [ "$env" = "dev" ] || [ "$env" = "prod" ] || usage
        if [ -n "$env" ]; then
            do_status "$env"
        else
            do_status dev
            do_status prod
        fi
        ;;
    *)
        usage
        ;;
esac
