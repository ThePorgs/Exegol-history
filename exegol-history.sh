#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
HISTORY_SCRIPT="$SCRIPT_DIR/exegol-history.py"

# Check if required files exist
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[-] Python virtual environment not found at: $VENV_PYTHON"
    echo "    Please ensure the virtual environment is properly set up."
    exit 1
fi

if [ ! -f "$HISTORY_SCRIPT" ]; then
    echo "[-] History script not found at: $HISTORY_SCRIPT"
    exit 1
fi

# Change this:
# PYTHON_SCRIPT="$VENV_PYTHON $HISTORY_SCRIPT"

# To array-style command:
PYTHON_CMD=("$VENV_PYTHON" "$HISTORY_SCRIPT")

case "$1" in
    export)
        if [ -z "$2" ]; then
            exit 1
        fi
        if VARS=$("${PYTHON_CMD[@]}" "$@"); then
            if [ -n "$VARS" ]; then
                eval "$VARS"
                NUM_VARS=$(echo "$VARS" | grep "export" | wc -l)
                echo "[+] Exported $NUM_VARS variables."
            else
                echo "[-] No variables to export."
            fi
        fi
        ;;
    env)
        "${PYTHON_CMD[@]}" env
        ;;
    *)
        "${PYTHON_CMD[@]}" "$@"
        ;;
esac 