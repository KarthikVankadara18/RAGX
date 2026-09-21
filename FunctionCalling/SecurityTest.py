from FunctionCalling.SecurityManager import SecurityManager

def main():

    security = SecurityManager()

    tests = [
        "MEMORY_LOOKUP",
        "MEMORY_SAVE",
        "MEMORY_UPDATE",
        "MEMORY_FORGET",
        "DOCUMENT_LOOKUP",
        "CALCULATION",
        "DELETE_DATABASE",
        "EXECUTE_SHELL",
    ]

    for action in tests:

        result = security.authorize_action(action)

        print()
        print("=" * 60)
        print("ACTION:", action)
        print("ALLOWED:", result["allowed"])
        print("REASON:", result["reason"])


if __name__ == "__main__":
    main()