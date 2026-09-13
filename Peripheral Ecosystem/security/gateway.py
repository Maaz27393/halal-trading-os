import logging

logger = logging.getLogger("PermissionGateway")

class PermissionGateway:
    """
    Security gateway verifying access rights and operation permissions 
    across Peripheral Ecosystem components.
    """

    def __init__(self):
        # Default allowed roles and capabilities
        self._permissions = {
            "strategy_engine": ["READ", "EXECUTE", "SEARCH"],
            "analyst_agent": ["READ", "SEARCH"]
        }
        logger.info("PermissionGateway initialized with standard role bindings.")

    def verify_permission(self, role: str, required_operation: str) -> bool:
        """Verify if a given role has access to a required operation."""
        allowed_ops = self._permissions.get(role, [])
        if required_operation in allowed_ops:
            logger.info(f"Permission granted for role '{role}' on operation '{required_operation}'.")
            return True
        logger.warning(f"Permission DENIED for role '{role}' on operation '{required_operation}'.")
        return False

    def grant_permission(self, role: str, operation: str) -> None:
        """Dynamically grant an operation permission to a role."""
        if role not in self._permissions:
            self._permissions[role] = []
        if operation not in self._permissions[role]:
            self._permissions[role].append(operation)
        logger.info(f"Granted operation '{operation}' to role '{role}'.")