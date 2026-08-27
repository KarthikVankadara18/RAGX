from Memory.MemoryLLMManager import (
    MemoryLLMManager
)


def main():

    session_id = "ragx-test-session"

    manager = MemoryLLMManager(
        session_id
    )

    print()
    print("=" * 60)
    print("RAGX PERSISTENT MEMORY TEST")
    print("=" * 60)

    while True:

        query = input(
            "\nYou: "
        ).strip()

        if query.lower() in {
            "exit",
            "quit"
        }:

            break

        answer = manager.chat(
            query
        )

        print()
        print(
            "Assistant:",
            answer
        )


if __name__ == "__main__":
    main()