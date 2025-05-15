from abc import ABC, abstractmethod
from typing import Optional

class Ingestor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def chunk_document(self, document: str, strategy: Optional[str]=None):
        pass    

class PDFIngestor(Ingestor):
    def __init__():
        pass

class DocxIngestor(Ingestor): 
    def __init__():
        pass

class CSVIngestor(Ingestor):
    def __init__():
        pass
    