from langchain_text_splitters import RecursiveCharacterTextSplitter
from Chunking.Strategies.BaseChunker import BaseChunker
from config import Config


class RecursiveChunker(BaseChunker):

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

    def chunk(self, documents):
        return self.splitter.split_documents(documents)