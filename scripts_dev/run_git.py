import subprocess
import sys

def run_git():
    try:
        result = subprocess.run(
            ['git', 'log', '-p', '-n', '2', '--', 'templates/financial_planning/wizard.html'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_git()
