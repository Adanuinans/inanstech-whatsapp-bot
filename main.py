# main.py
from bot.driver import launch_browser
from bot.state_manager import StateManager
from bot.router import Router
from bot.simple_watcher import watch_messages
from bot.followup import start_followup_manager
from bot.interaction_recorder import InteractionRecorder
from dashboard.app import app
import threading

def run_dashboard():
    app.run(port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    # Start dashboard in background
    dashboard_thread = threading.Thread(target=run_dashboard)
    dashboard_thread.start()

    # Launch browser
    driver = launch_browser()

    # Initialize state and router
    state = StateManager()
    router = Router(state)

    # Start follow-up manager (background thread)
    followup_manager = start_followup_manager(driver, state, router)
    
    # Set the instance for the InteractionRecorder
    InteractionRecorder.set_instance(followup_manager)

    # Start watching messages
    watch_messages(driver, router, state)