from datetime import datetime, timezone
from bson import ObjectId

from RAGChatBot.Memory.PersistentMemory import PersistentMemory
from Backend.Security.Password import hash_password

class UserModel:
    def __init__(self, persistent_memory= None):
        self.persistent_memory = persistent_memory or PersistentMemory()
        self.users_collection = self.persistent_memory.users_collection

    def create_user(self, email: str, password: str):
        email= email.strip().lower()

        if self.users_collection.find_one({"email": email}):
            raise ValueError("User with this email already exists.")
        
        document = {
            "email": email,
            "password_hash": hash_password(password),
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }

        result= self.users_collection.insert_one(document)
        print(f"User created with email: {email}, user_id: {result.inserted_id}")
        
        return{
            "user_id": str(result.inserted_id),
            "email": email,
        }
        
    def get_user_by_email(self, email: str):
        email = email.strip().lower()
        return self.users_collection.find_one({"email": email})

    def get_user_by_id(self, user_id):
        return self.persistent_memory.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )