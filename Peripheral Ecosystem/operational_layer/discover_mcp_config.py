import os
import json
import sys

def discover_configs():
    print("=" * 60)
    print("MCP CONFIGURATION DISCOVERY")
    print("=" * 60)

    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Mohammed Muzameel")
    
    # Common local MCP client configuration paths
    candidate_paths = {
        "Claude Desktop": os.path.join(user_profile, "AppData", "Roaming", "Claude", "claude_desktop_config.json"),
        "OpenCode / Custom Agent": os.path.join(user_profile, ".config", "opencode", "config.json"), # Example local path
        "Cursor / IDE Agent": os.path.join(user_profile, ".cursor", "mcp.json"),
    }

    found_any = False
    for client_name, path in candidate_paths.items():
        print(f"\nChecking [{client_name}]:")
        print(f"Path: {path}")
        if os.path.exists(path):
            found_any = True
            print(f"Status: FOUND ✅")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print("Existing Servers Registered:")
                    servers = data.get("mcpServers", data.get("servers", {}))
                    for s_name in servers.keys():
                        print(f"  - {s_name}")
            except Exception as e:
                print(f"  (Error reading config file: {e})")
        else:
            print("Status: NOT FOUND ❌")

    if not found_any:
        print("\nNote: No standard config files found in typical default paths. Your active client might be running via a custom workspace or command-line flag.")

if __name__ == "__main__":
    discover_configs()