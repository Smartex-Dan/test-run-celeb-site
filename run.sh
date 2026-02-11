
#!/bin/bash
# run.sh - start Membership Monarch Flask app and open browser

# ---- Step 1: Activate virtual environment ----
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Skipping..."
fi

# ---- Step 2: Set Flask environment variables ----
export FLASK_APP=app.py
export FLASK_ENV=development  # Change to 'production' when deploying

# ---- Step 3: Optional: Ensure templates/static are present ----
if [ ! -d "templates" ]; then
    echo "Warning: 'templates' folder not found!"
fi
if [ ! -d "static" ]; then
    echo "Warning: 'static' folder not found!"
fi

# ---- Step 4: Start Flask in the background ----
echo "Starting Membership Monarch..."
flask run --host=0.0.0.0 --port=5000 &

# ---- Step 5: Wait a few seconds, then open browser ----
sleep 3  # wait for server to start
echo "Opening browser..."
if command -v xdg-open >/dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v open >/dev/null; then
    open http://127.0.0.1:5000
else
    echo "Please open http://127.0.0.1:5000 manually"
fi

# ---- Step 6: Bring Flask back to foreground ----
fg
