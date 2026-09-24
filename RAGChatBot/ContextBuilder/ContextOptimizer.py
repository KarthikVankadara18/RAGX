# import difflib
# from config import Config

# class ContextOptimizer:

#     def __init__(self):
#         print("Context Optimizer Initialized")

#     def optimize(self, results):

#         if not results:
#             return []

#         results = self.remove_duplicates(results)
#         results = self.remove_near_duplicates(results)
#         results = self.filter_short_chunks(results)
#         results = self.filter_by_relevance(results)
#         return results

#     def remove_duplicates(self, results):

#         seen = set()
#         optimized = []

#         for result in results:

#             text = result["text"].strip()

#             if not text:
#                 continue

#             normalized_text = " ".join(text.split())

#             duplicate_key = normalized_text.lower()

#             if duplicate_key in seen:
#                 continue

#             seen.add(duplicate_key)

#             optimized.append(result)

#         return optimized

#     def remove_near_duplicates(self, results):

#         kept = []

#         for candidate in results:

#             is_duplicate = False

#             for existing in kept:

#                 similarity = difflib.SequenceMatcher(
#                     None,
#                     candidate["text"],
#                     existing["text"]
#                 ).ratio()

#                 if similarity >= Config.CONTEXT_DEDUP_THRESHOLD:
#                     is_duplicate = True
#                     break

#             if not is_duplicate:
#                 kept.append(candidate)

#         return kept

#     def filter_short_chunks(self, results):

#         return [
#             result
#             for result in results
#             if len(result["text"].strip()) >= Config.MIN_CHUNK_CHARS
#         ]

#     def filter_by_relevance(self, results):

#         return [
#             result
#             for result in results
#             if result.get("rerank_score", 0) >= Config.MIN_RERANK_SCORE
#         ]

import difflib

from config import Config


class ContextOptimizer:

    def __init__(self):

        print(
            "Context Optimizer Initialized"
        )

    def optimize(self, results):

        if not results:
            return []

        results = self.remove_duplicates(
            results
        )

        results = self.remove_near_duplicates(
            results
        )

        results = self.remove_heading_only_chunks(
            results
        )

        results = self.filter_short_chunks(
            results
        )

        return results

    def remove_duplicates(self, results):

        seen = set()
        optimized = []

        for result in results:

            text = result.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            normalized_text = (
                " ".join(
                    text.split()
                )
            )

            duplicate_key = (
                normalized_text.lower()
            )

            if duplicate_key in seen:
                continue

            seen.add(
                duplicate_key
            )

            optimized.append(
                result
            )

        return optimized

    def remove_near_duplicates(
        self,
        results
    ):

        kept = []

        for candidate in results:

            candidate_text = (
                candidate["text"].strip()
            )

            is_duplicate = False

            for existing in kept:

                existing_text = (
                    existing["text"].strip()
                )

                similarity = (
                    difflib.SequenceMatcher(
                        None,
                        candidate_text,
                        existing_text
                    ).ratio()
                )

                if (
                    similarity
                    >= Config.CONTEXT_DEDUP_THRESHOLD
                ):

                    is_duplicate = True
                    break

            if not is_duplicate:

                kept.append(
                    candidate
                )

        return kept

    def remove_heading_only_chunks(
        self,
        results
    ):

        optimized = []

        for result in results:

            text = result.get(
                "text",
                ""
            ).strip()

            metadata = result.get(
                "metadata",
                {}
            )

            section = metadata.get(
                "section"
            )

            if not section:

                optimized.append(
                    result
                )

                continue

            normalized_text = (
                " ".join(
                    text.split()
                ).lower()
            )

            normalized_section = (
                " ".join(
                    section.split()
                ).lower()
            )

            remaining_text = (
                normalized_text
                .replace(
                    normalized_section,
                    "",
                    1
                )
                .strip(
                    " .:-"
                )
            )

            if not remaining_text:

                continue

            optimized.append(
                result
            )

        return optimized

    def filter_short_chunks(
        self,
        results
    ):

        optimized = []

        for result in results:

            text = result.get(
                "text",
                ""
            ).strip()

            if len(text) < Config.MIN_CHUNK_CHARS:

                continue

            optimized.append(
                result
            )

        return optimized