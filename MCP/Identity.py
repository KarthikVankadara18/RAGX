class MCPIdentityError(Exception):
    pass

class MCPIdentity:

    def __init__(self, user_id: str, session_id: str | None = None):
        if not user_id or not user_id.strip():
            raise MCPIdentityError(
                "Authenticated user identity is required."
            )

        self.user_id = user_id
        self.session_id = session_id

    def get_user_id(self):
        return self.user_id

    def get_session_id(self):
        return self.session_id