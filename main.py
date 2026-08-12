# from DocumentManger.DocumentManger import DocManger
# from Embeddings.EmbeddingManager import EmbeddingManager
# from VectorDB.Faiss_Manager import FAISSManager
# from VectorDB.MetaData_Store import MetadataStore

# def main():
#     file_path = "Data/PDF/RAG_Sample_Document.pdf"

#     manager = DocManger()
#     embedding_manager= EmbeddingManager()
#     metadata_store = MetadataStore()
#     faiss_manager = FAISSManager()
    
#     chunks = manager.process_documents(file_path)
#     # for i, chunk in enumerate(chunks):
#     #     print("=" * 50)
#     #     print(f"Chunk {i+1}")
#     #     print(chunk.metadata)
    
#     embedding_result= embedding_manager.GenerateEmbeeding(chunks)
#     print()
#     print("=" * 50)
#     print("Total Chunks :", len(chunks))
#     print("Embeddings Shape :", embedding_result.shape)

#     faiss_manager.add_embeddings(embedding_result)
#     faiss_manager.save_index()
    
#     metadata_store.save(chunks)
#     print("=" * 50) 
# if __name__ == "__main__":
#     main()


# from Retrieval.Retrieval import Retriever

# def main():

#     retriever = Retriever()
#     results = retriever.retrieve(
#         "What is Retrieval Augmented Generation?"
#     )
#     print()
#     print("=" * 50)
#     print("Retrieved Chunks")
#     print("=" * 50)

#     for result in results:
#         print(result["text"])
#         print("-" * 50)

# if __name__ == "__main__":

#     main()


from DocumentManger.DocumentManger import DocManger


def main():

    file_path = "Data/PDF/PRACTICAL-GUIDE-TO-BUILDING-RETRIEVAL-AUGMENTED-GENERATION-RAG.pdf"

    manager = DocManger()

    profile = manager.load_documents(file_path)

    print()
    print("=" * 60)
    print("CHUNKING RESULTS")
    print("=" * 60)

    print(
        "Total Chunks :",
        len(profile.chunks)
    )

    for chunk in profile.chunks[:10]:

        print()
        print("Chunk ID :", chunk.chunk_id)

        print(
            "Page     :",
            chunk.metadata["page"]
        )

        print(
            "Section  :",
            chunk.metadata["section"]
        )

        print(
            "Subsection :",
            chunk.metadata["subsection"]
        )

        print("Text     :")
        print(chunk.text)

        print("-" * 60)


if __name__ == "__main__":
    main()