#!/bin/bash

# Ruta a tu entorno virtual
VENV_PATH="./env/bin/activate"

# --- Terminal 1: FastAPI
osascript <<EOF
tell application "Terminal"
    do script "cd $(pwd); source $VENV_PATH; uvicorn api.app:app --reload --port 8000"
end tell
EOF

# --- Terminal 2: consumer.py
osascript <<EOF
tell application "Terminal"
    do script "cd $(pwd); source $VENV_PATH; python consumer/consumer.py"
end tell
EOF

# --- Terminal 3: consumer_results.py
osascript <<EOF
tell application "Terminal"
    do script "cd $(pwd); source $VENV_PATH; python consumer/consumer_results.py"
end tell
EOF

# --- Terminal 4: final_aggregator.py
osascript <<EOF
tell application "Terminal"
    do script "cd $(pwd); source $VENV_PATH; python consumer/final_aggregator.py"
end tell
EOF

echo "✅ Todas las ventanas fueron lanzadas."
