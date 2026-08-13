import re

class DocumentCleaner:

    def __init__(self):
        print("Document Cleaner Initialized")

    def clean_documents(self, documents):
        cleaned_documents = []
        for document in documents:
            text = document.page_content
            text = self.clean_text(text)
            document.page_content = text
            cleaned_documents.append(document)
        return cleaned_documents

    def clean_text(self, text: str):
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )
        return text.strip()