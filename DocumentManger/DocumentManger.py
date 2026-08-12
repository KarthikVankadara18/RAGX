from Loaders.LoadFactor import LoaderFactory
from DocumentManger.DocumentClean import DocumentCleaner
from Chunking.ChunkingManager import ChunkManager
from Models.DocumentProfile import DocumentProfile
from DocumentAnalyzer.DocAnalyzer import DocumentAnalyzer

class DocManger:
    def __init__(self):
        print("Document Manager initilized the document process")
        self.cleaner = DocumentCleaner()
        self.chunking_manager = ChunkManager()
        self.analyzer = DocumentAnalyzer()

    def load_documents(self, file_path: str):
        profile = DocumentProfile(
            file_path=file_path
        )
        loader = LoaderFactory.get_loader(
            file_path
        )
        documents = loader.load(
            file_path
        )

        profile.documents = documents
        
        profile.documents = (
            self.cleaner.clean_documents(
                profile.documents
            )
        )
        profile = self.analyzer.analyze(
            profile
        )
        profile = self.chunking_manager.create_chunks(
            profile
        )
        return profile