from pymongo import MongoClient
from config import Config

class PersistentMemory:

    def __init__(self):

        print(
            "Persistent Memory Initialized"
        )

        if not Config.MONGODB_URI:
            raise ValueError(
                "MONGODB_URI is not configured."
            )

        self.client = MongoClient(
            Config.MONGODB_URI
        )

        self.database = self.client[
            Config.MONGODB_DATABASE
        ]

        self.collection = self.database[
            Config.MONGODB_COLLECTION
        ]

        self.client.admin.command(
            "ping"
        )

        print(
            "MongoDB Connected Successfully."
        )

    def save_message(
        self,
        session_id,
        role,
        content
    ):

        document = {

            "session_id": session_id,

            "role": role,

            "content": content
        }

        self.collection.insert_one(
            document
        )

    def load_messages(
        self,
        session_id
    ):

        cursor = (
            self.collection
            .find(
                {
                    "session_id": session_id,
                    "role": {
                        "$in": [
                            "user",
                            "assistant"
                        ]
                    }
                }
            )
            .sort(
                "_id",
                1
            )
        )

        messages = []

        for document in cursor:

            messages.append(
                {
                    "role": document["role"],
                    "content": document["content"]
                }
            )

        return messages
    
    def save_summary(
        self,
        session_id,
        summary
    ):

        self.collection.update_one(
            {
                "session_id": session_id,
                "role": "summary"
            },
            {
                "$set": {
                    "content": summary
                }
            },
            upsert=True
        )

    def load_summary(
        self,
        session_id
    ):

        document = (
            self.collection.find_one(
                {
                    "session_id": session_id,
                    "role": "summary"
                }
            )
        )

        if not document:
            return ""

        return document.get(
            "content",
            ""
        )

    def clear_session(
        self,
        session_id
    ):

        self.collection.delete_many(
            {
                "session_id": session_id
            }
        )

    def close(self):

        self.client.close()