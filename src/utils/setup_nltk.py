import nltk
import ssl

def setup_nltk():
    """
    Pobiera wymagane zasoby NLTK
    """
    try:
        # Próba obejścia problemów z SSL na niektórych systemach
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        # Pobieranie wymaganych zasobów
        resources = [
            'punkt',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words',
            'stopwords',
            'wordnet',
            'omw-1.4'
        ]
        
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
                print(f"Pobrano zasób NLTK: {resource}")
            except Exception as e:
                print(f"Błąd podczas pobierania zasobu {resource}: {str(e)}")
                
    except Exception as e:
        print(f"Błąd podczas konfiguracji NLTK: {str(e)}")

if __name__ == "__main__":
    setup_nltk() 