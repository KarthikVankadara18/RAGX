from FunctionCalling.FunctionCallingManager import (
    FunctionCallingManager
)


def main():

    manager = FunctionCallingManager()

    query = input(
        "\nAsk something about the document: "
    ).strip()

    result = manager.run(
        query
    )

    print()
    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    print(
        result["answer"]
    )

    print()
    print("=" * 60)
    print("TOOL USED")
    print("=" * 60)

    print(
        result["tool_called"]
    )


if __name__ == "__main__":
    main()