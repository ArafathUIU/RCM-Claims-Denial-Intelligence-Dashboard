"""Capture screenshots of Streamlit dashboard pages using Playwright."""
import subprocess
import time
import os
import sys

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8501"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

PAGES = {
    "01_overview": "/overview",
    "02_payer_analysis": "/payer_analysis",
    "03_denial_reasons": "/denial_reasons",
    "04_revenue_recovery": "/revenue_recovery",
    "05_provider_aging": "/provider_aging",
}


def main():
    print("Starting Streamlit server...")
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py",
         "--server.headless", "true", "--server.port", "8501"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )

    time.sleep(8)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})

        for name, path in PAGES.items():
            print(f"Capturing: {name} ...")
            page = context.new_page()
            try:
                page.goto(f"{BASE_URL}{path}", timeout=30000, wait_until="load")
                page.wait_for_timeout(8000)
                page.screenshot(
                    path=os.path.join(SCREENSHOT_DIR, f"{name}.png"),
                    full_page=True,
                )
                print(f"  Saved: {name}.png")
            except Exception as e:
                print(f"  Failed: {e}")
            finally:
                page.close()

        browser.close()

    server.terminate()
    server.wait()
    print("Done.")


if __name__ == "__main__":
    main()
