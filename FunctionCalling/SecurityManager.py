class SecurityManager:

    ALLOWED_ACTIONS = {
        "MEMORY_LOOKUP",
        "MEMORY_SAVE",
        "MEMORY_UPDATE",
        "MEMORY_FORGET",
        "DOCUMENT_LOOKUP",
        "CALCULATION",
    }

    PROTECTED_ACTIONS = {
        "MEMORY_LOOKUP",
        "MEMORY_SAVE",
        "MEMORY_UPDATE",
        "MEMORY_FORGET",
    }

    def __init__(self, runtime_context):
        print("Security Manager Initialized")
        self.runtime_context = runtime_context

    def authorize_action(self, action):

        if action not in self.ALLOWED_ACTIONS:
            return {
                "allowed": False,
                "reason": f"Action '{action}' is not authorized."
            }

        if action in self.PROTECTED_ACTIONS:
            if not self.runtime_context.user_id:
                return {
                    "allowed": False,
                    "reason": "Authenticated user identity is required."
                }

        return {
            "allowed": True,
            "reason": "Action authorized."
        }

    def get_user_id(self):
        return self.runtime_context.user_id

    def get_session_id(self):
        return self.runtime_context.session_id