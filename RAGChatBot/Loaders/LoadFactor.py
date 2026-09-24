from pathlib import Path
from Loaders.PDF_Loader import PDFLoader

class LoaderFactory:
    LOADERS = {
        ".pdf": PDFLoader,
    }

    @staticmethod
    def get_loader(file_path: str):

        extension = Path(file_path).suffix.lower()

        loader_class = LoaderFactory.LOADERS.get(extension)

        if loader_class is None:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return loader_class()