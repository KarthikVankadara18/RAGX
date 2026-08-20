from Retrieval.Retrieval import Retriever
from ContextBuilder.ContextOptimizer import ContextOptimizer
from PromptBuilder.PromptBuilder import PromptBuilder
from LLM.LLMManager import LLMManager

def main():

    query = input(
        "\nEnter your question: "
    ).strip()

    if not query:
        raise ValueError(
            "Question cannot be empty."
        )

    retriever = Retriever()

    optimizer = ContextOptimizer()

    prompt_builder = PromptBuilder()

    llm = LLMManager()

    results = retriever.retrieve(
        query
    )

    optimized_results = (
        optimizer.optimize(
            results
        )
    )

    prompt_data = (
        prompt_builder.build(
            query,
            optimized_results
        )
    )

    answer = llm.generate_response(
        prompt_data["prompt"]
    )

    print()
    print("=" * 70)
    print("RAGX ANSWER")
    print("=" * 70)

    print(answer)

    print()
    print("=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in prompt_data["sources"]:

        print(
            f"\nSource {source['source_number']}"
        )

        print(
            f"Chunk ID    : "
            f"{source['chunk_id']}"
        )

        print(
            f"Page       : "
            f"{source['page']}"
        )

        print(
            f"Section    : "
            f"{source['section']}"
        )

        print(
            f"Subsection : "
            f"{source['subsection']}"
        )

        print(
            f"Source     : "
            f"{source['source']}"
        )

        print("-" * 70)


if __name__ == "__main__":
    main()