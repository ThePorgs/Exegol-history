#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PYTHON_SCRIPT="$SCRIPT_DIR/exegol-history.py"

case "$1" in
    export)
        if [ -z "$2" ]; then
            exit 1
        fi
        if VARS=$("$PYTHON_SCRIPT" export "$@"); then
            if [ -n "$VARS" ]; then
                eval "$VARS"
                NUM_VARS=$(echo "$VARS" | wc -l)
                echo "[+] Exported $NUM_VARS variables."
            else
                echo "[-] No variables to export."
            fi
        fi
        ;;
    env)
        "$PYTHON_SCRIPT" env "$@"
        ;;
    *)
        "$PYTHON_SCRIPT" "$@"
        ;;
esac 