#!/bin/bash

echo "========================================"
echo "Voice Command AI - Quick Launcher"
echo "========================================"
echo ""

python3 run.py

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    read -p "Press Enter to exit..."
fi

exit $exit_code