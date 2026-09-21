class RecoveryManager:

    RECOVERABLE_ACTIONS = {
        "MEMORY_UPDATE",
        "MEMORY_FORGET",
    }

    def __init__(self):
        print("Recovery Manager Initialized")

    def can_recover(self, step, error):
        action = step.get("action")

        if action not in self.RECOVERABLE_ACTIONS:
            return False

        if not error:
            return False

        error_text = str(error).lower()

        recoverable_errors = [
            "no memory id found",
            "memory not found",
            "invalid memory",
            "memory_id",
        ]

        return any(
            message in error_text
            for message in recoverable_errors
        )

    def create_recovery_step(self, failed_step):
        action = failed_step.get("action")

        if action not in self.RECOVERABLE_ACTIONS:
            return None

        query = failed_step.get("query")

        return {
            "step": failed_step.get("step"),
            "action": "MEMORY_LOOKUP",
            "query": query,
            "reason": (
                f"Recovery lookup required before "
                f"{action}."
            ),
        }