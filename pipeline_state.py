import json
import os

STATE_FILE = 'pipeline_state.json'


def get_current_state():
    """
    Reads how many days of data have been released so far.
    If this is the first run, starts fresh.
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"days_released": 0, "last_run": None}


def save_state(days_released, last_run):
    """Saves progress so next time we know where to continue from."""
    with open(STATE_FILE, 'w') as f:
        json.dump({"days_released": days_released, "last_run": str(last_run)}, f)