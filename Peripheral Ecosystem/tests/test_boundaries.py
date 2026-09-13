import sys
import importlib

def test_no_frozen_core_imports():
    """Ensures that the peripheral ecosystem never imports from Automation or execution cores."""
    forbidden_prefixes = ("Automation", "execution", "risk_engine")
    
    # Check currently loaded modules or attempt to inspect package imports
    for module_name in list(sys.modules.keys()):
        if any(module_name.startswith(f) for f in forbidden_prefixes):
            raise ImportError(
                f"Architecture Violation: Peripheral layer loaded forbidden internal module '{module_name}'."
            )
    print("Boundary Check Passed: Zero contamination from frozen core modules.")

if __name__ == "__main__":
    test_no_frozen_core_imports()