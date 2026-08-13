from Retrieval.Retrieval import Retriever

def main():

    retriever = Retriever()

    results = retriever.retrieve(
        "What is Retrieval Augmented Generation?"
    )

    print()
    print("=" * 60)
    print("FINAL RETRIEVED RESULTS")
    print("=" * 60)

    for result in results:

        print(
            f"\nChunk ID : {result['chunk_id']}"
        )

        print(
            f"Distance : {result['distance']}"
        )

        print(
            f"Page : "
            f"{result['metadata'].get('page')}"
        )

        print(
            f"Section : "
            f"{result['metadata'].get('section')}"
        )

        print(
            f"Subsection : "
            f"{result['metadata'].get('subsection')}"
        )

        print(
            f"\nText:\n{result['text']}"
        )

        print("-" * 60)


if __name__ == "__main__":
    main()