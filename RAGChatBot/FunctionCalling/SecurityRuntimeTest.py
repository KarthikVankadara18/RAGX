from FunctionCalling.SecurityManager import SecurityManager
from FunctionCalling.RuntimeContext import RuntimeContext

def main():

    runtime_context = RuntimeContext(
        user_id="user_001",
        session_id="security_test"
    )

    security = SecurityManager(runtime_context)

    print()
    print("=" * 60)
    print("AUTHORIZED USER")
    print("=" * 60)

    print("User ID     :", security.get_user_id())
    print("Session ID  :", security.get_session_id())

    print()
    print("MEMORY_LOOKUP:")
    print(security.authorize_action("MEMORY_LOOKUP"))

    print()
    print("DOCUMENT_LOOKUP:")
    print(security.authorize_action("DOCUMENT_LOOKUP"))

    print()
    print("UNKNOWN_ACTION:")
    print(security.authorize_action("DELETE_DATABASE"))

    print()
    print("=" * 60)
    print("MISSING IDENTITY TEST")
    print("=" * 60)

    empty_context = RuntimeContext(
        user_id="",
        session_id="security_test"
    )

    empty_security = SecurityManager(empty_context)

    print(
        empty_security.authorize_action(
            "MEMORY_LOOKUP"
        )
    )


if __name__ == "__main__":
    main()