from datetime import datetime, timedelta, timezone

from bson import ObjectId
from pymongo import MongoClient

from config import Config


class PersistentMemory:

    def __init__(self):
        print("Persistent Memory Initialized")

        if not Config.MONGODB_URI:
            raise ValueError("MONGODB_URI is not configured.")

        self.client = MongoClient(Config.MONGODB_URI)
        self.database = self.client[Config.MONGODB_DATABASE]
        self.collection = self.database[Config.MONGODB_COLLECTION]

        self.long_term_collection = self.database["long_term_memories"]

        self.client.admin.command("ping")
        print("MongoDB Connected Successfully.")

        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index([("session_id", 1), ("role", 1)])
        self.long_term_collection.create_index([("user_id", 1), ("status", 1)])
        self.long_term_collection.create_index([("user_id", 1), ("session_id", 1)])
        self.long_term_collection.create_index([("user_id", 1), ("type", 1), ("status", 1)])


    def save_message(self, session_id, role, content):
        self.collection.insert_one({
            "session_id": session_id,
            "role": role,
            "content": content,
        })

    def load_messages(self, session_id):
        cursor = (
            self.collection
            .find({
                "session_id": session_id,
                "role": {"$in": ["user", "assistant"]},
            })
            .sort("_id", 1)
        )

        return [
            {"role": document["role"], "content": document["content"]}
            for document in cursor
        ]

    def save_summary(self, session_id, summary):
        self.collection.update_one(
            {"session_id": session_id, "role": "summary"},
            {"$set": {"content": summary}},
            upsert=True,
        )

    def load_summary(self, session_id):
        document = self.collection.find_one({
            "session_id": session_id,
            "role": "summary",
        })
        return document.get("content", "") if document else ""

    def clear_session(self, session_id):
        self.collection.delete_many({"session_id": session_id})


    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    def save_long_term_memory(
        self,
        user_id,
        session_id,
        content,
        memory_type="fact",
        importance=3,
    ):
        now = self._now()
        document = {
            "user_id": user_id,
            "session_id": session_id,
            "type": memory_type,
            "content": content,
            "importance": max(1, min(5, int(importance))),
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "last_accessed": now,
        }
        result = self.long_term_collection.insert_one(document)
        return str(result.inserted_id)

    def get_memory_by_id(self, memory_id):
        try:
            document = self.long_term_collection.find_one({"_id": ObjectId(memory_id)})
        except Exception:
            return None

        if not document:
            return None

        return self._serialize_memory(document)

    def _serialize_memory(self, document):
        return {
            "memory_id": str(document["_id"]),
            "user_id": document.get("user_id"),
            "session_id": document.get("session_id"),
            "type": document.get("type", "fact"),
            "content": document.get("content", ""),
            "importance": int(document.get("importance", 3)),
            "status": document.get("status", "active"),
            "created_at": document.get("created_at"),
            "updated_at": document.get("updated_at"),
            "last_accessed": document.get("last_accessed"),
        }

    def get_all_memories(
        self,
        status="active",
    ):
        query = {}
        if status is not None:
            query["status"] = status
        cursor = self.long_term_collection.find(query).sort("updated_at", -1)
        return [self._serialize_memory(document) for document in cursor]

    def get_user_memories(
        self,
        user_id,
        session_id=None,
        scope="user",
        status="active",
    ):
        query = {"user_id": user_id}

        if status is not None:
            query["status"] = status

        if scope == "session":
            query["session_id"] = session_id
        elif scope not in {"user", "all"}:
            raise ValueError("scope must be 'user', 'session', or 'all'.")

        cursor = self.long_term_collection.find(query).sort("updated_at", -1)
        return [self._serialize_memory(document) for document in cursor]

    def update_long_term_memory(
        self,
        memory_id,
        content,
        memory_type=None,
        importance=None,
        status="active",
    ):
        update = {
            "content": content,
            "status": status,
            "updated_at": self._now(),
            "last_accessed": self._now(),
        }

        if memory_type is not None:
            update["type"] = memory_type
        if importance is not None:
            update["importance"] = max(1, min(5, int(importance)))

        try:
            result = self.long_term_collection.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": update},
            )
        except Exception:
            return False

        return result.modified_count > 0

    def set_memory_status(self, memory_id, status):
        if status not in {"active", "archived", "forgotten"}:
            raise ValueError("Invalid memory status.")

        try:
            result = self.long_term_collection.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": {"status": status, "updated_at": self._now()}},
            )
        except Exception:
            return False

        return result.modified_count > 0

    def touch_memory(self, memory_id):
        try:
            result = self.long_term_collection.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": {"last_accessed": self._now()}},
            )
        except Exception:
            return False

        return result.modified_count > 0

    def archive_memory(self, memory_id):
        return self.set_memory_status(memory_id, "archived")

    def forget_memory(self, memory_id):
        return self.set_memory_status(memory_id, "forgotten")

    def apply_lifecycle(
        self,
        user_id,
        archive_after_days=180,
        forget_after_days=365,
    ):
        now = self._now()
        archive_cutoff = now - timedelta(days=archive_after_days)
        forget_cutoff = now - timedelta(days=forget_after_days)

        forget_cutoff_important = now - timedelta(days=forget_after_days * 2)

        archive_result = self.long_term_collection.update_many(
            {
                "user_id": user_id,
                "status": "active",
                "last_accessed": {"$lt": archive_cutoff},
                "importance": {"$lte": 2},
            },
            {"$set": {"status": "archived", "updated_at": now}},
        )

        forget_result = self.long_term_collection.update_many(
            {
                "user_id": user_id,
                "status": "archived",
                "$or": [
                    {"last_accessed": {"$lt": forget_cutoff}},
                    {
                        "last_accessed": {"$lt": forget_cutoff_important},
                        "importance": {"$gte": 4},
                    },
                ],
            },
            {"$set": {"status": "forgotten", "updated_at": now}},
        )

        return {
            "archived": archive_result.modified_count,
            "forgotten": forget_result.modified_count,
        }

    def close(self):
        self.client.close()
