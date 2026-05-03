from agent.main import run

if __name__ == "__main__":
    result = run("configs/config.yaml")
    print("Agent run complete.")
    print("CSV:", result["csv"])
    print("HTML:", result["html"])
