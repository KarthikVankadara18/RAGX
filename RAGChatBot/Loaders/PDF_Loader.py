from langchain_community.document_loaders import PyPDFLoader

class PDFLoader:
    def __init__(self):
        print("Initialized Loader")

    def load(self, pdf_path: str):
        loader= PyPDFLoader(pdf_path)
        documents= loader.load()
        
        return documents