"""
Moduł zawierający wyjątki używane w aplikacji.
"""

class PDFSearchError(Exception):
    """Bazowy wyjątek dla aplikacji"""
    pass

class FileOperationError(PDFSearchError):
    """Błąd podczas operacji na plikach"""
    pass

class PDFProcessingError(PDFSearchError):
    """Błąd podczas przetwarzania pliku PDF"""
    pass

class IndexingError(PDFSearchError):
    """Błąd podczas indeksowania dokumentów"""
    pass

class SearchError(PDFSearchError):
    """Błąd podczas wyszukiwania"""
    pass

class ConfigurationError(PDFSearchError):
    """Błąd konfiguracji"""
    pass 