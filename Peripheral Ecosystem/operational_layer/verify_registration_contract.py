import os
import json
import sys

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
REG_PATH = rf"{VAULT_ROOT}\Peripheral Ecosystem\operational_layer\nse_mcp_registration.json"

def verify_contract():
    print("=" * 60)
    print("REGISTRATION CONTRACT VERIFICATION")
    print("=" * 60)

    if not os.path.exists(REG_PATH):
        print(f"Error: Registration contract not found at {REG_PATH}")
        sys.exit(1)

    print(f"\n[1] Reading registration contract from:\n{REG_PATH}")
    with open(REG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    print(f"Total Servers Registered: {len(servers)}")

    for name, details in servers.items():
        print(f"\n-> Server ID: '{name}'")
        print(f"   Command : {details.get('command')}")
        print(f"   Args    : {details.get('args')}")
        if "env" in details:
            print(f"   Env     : {details.get('env')}")
            
        # Validate target script file existence
        args = details.get("args", [])
        if args:
            target_script = args[0]
            exists = os.path.exists(target_script)
            print(f"   Script Target Exists: {exists} ({target_script})")
            assert exists, f"Target script missing for {name}"

    print("\n" + "=" * 60)
    print("REGISTRATION CONTRACT IS STRUCTURALLY SOUND & VERIFIED")
    print("=" * 60)

if __name__ == "__main__":
    verify_contract()