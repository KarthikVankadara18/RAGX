class ConversationMemory:

    def __init__(
        self,
        persistent_memory,
        session_id,
        max_recent_messages=6
    ):

        print(
            "Conversation Memory Initialized"
        )

        self.persistent_memory = (
            persistent_memory
        )

        self.session_id = session_id

        self.max_recent_messages = (
            max_recent_messages
        )

        self.messages = (
            self.persistent_memory
            .load_messages(
                session_id
            )
        )

        self.summary = (
            self.persistent_memory
            .load_summary(
                session_id
            )
        )

    def add_user_message(
        self,
        message
    ):

        item = {
            "role": "user",
            "content": message
        }

        self.messages.append(
            item
        )

        self.persistent_memory.save_message(
            self.session_id,
            "user",
            message
        )

    def add_assistant_message(
        self,
        message
    ):

        item = {
            "role": "assistant",
            "content": message
        }

        self.messages.append(
            item
        )

        self.persistent_memory.save_message(
            self.session_id,
            "assistant",
            message
        )

    def get_recent_messages(self):

        return self.messages[
            -self.max_recent_messages:
        ]

    def get_messages(self):

        return self.messages.copy()

    def get_summary(self):

        return self.summary

    def update_summary(
        self,
        summary
    ):

        self.summary = summary

        self.persistent_memory.save_summary(
            self.session_id,
            summary
        )

    def clear(self):

        self.messages.clear()

        self.summary = ""

        self.persistent_memory.clear_session(
            self.session_id
        )

    def message_count(self):

        return len(
            self.messages
        )
