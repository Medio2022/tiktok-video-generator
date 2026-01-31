"""
Décorateur de retry avec backoff exponentiel
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Décorateur pour retry automatique avec backoff exponentiel
    
    Args:
        max_attempts: Nombre maximum de tentatives
        delay: Délai initial en secondes
        backoff: Facteur de multiplication du délai
        exceptions: Tuple d'exceptions à capturer
        
    Usage:
        @retry(max_attempts=3, delay=2, backoff=2)
        def my_function():
            # Code qui peut échouer
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"❌ {func.__name__} a échoué après {max_attempts} tentatives: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"⚠️  {func.__name__} a échoué (tentative {attempt}/{max_attempts}): {e}"
                    )
                    logger.info(f"⏳ Nouvelle tentative dans {current_delay:.1f}s...")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Ne devrait jamais arriver ici
            raise last_exception
        
        return wrapper
    return decorator


# Exemple d'utilisation
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    @retry(max_attempts=3, delay=1, backoff=2)
    def test_function():
        """Fonction de test qui échoue 2 fois puis réussit"""
        import random
        if random.random() < 0.7:
            raise ValueError("Erreur aléatoire")
        return "Succès!"
    
    try:
        result = test_function()
        print(f"✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Échec final: {e}")
