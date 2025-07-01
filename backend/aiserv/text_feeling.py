import re
import unidecode
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nrclex import NRCLex
from deep_translator import GoogleTranslator

# Descargar los recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')  # Descargamos las stopwords

# Inicializar el traductor de Google
translator = GoogleTranslator(source='auto', target='en')


# 1. Limpiar el texto (eliminar signos de puntuación, números, acentos, y convertir a minúsculas)
def limpiar_texto(texto):
    texto_sin_puntuacion = re.sub(r'[^\w\s]', '', texto)
    texto_sin_numeros = re.sub(r'\d+', '', texto_sin_puntuacion)
    texto_minusculas = texto_sin_numeros.lower()
    texto_normalizado = unidecode.unidecode(texto_minusculas)
    return texto_normalizado


# 2. Tokenizar el texto en palabras individuales
def tokenizar_texto(texto):
    texto_limpio = limpiar_texto(texto)
    tokens = texto_limpio.split()
    return tokens


# 3. Eliminar las stopwords en inglés
def eliminar_stopwords_en(tokens):
    stop_words = set(stopwords.words('english'))  # Usamos stopwords en inglés
    tokens_filtrados = [word for word in tokens if word not in stop_words]
    return tokens_filtrados


# 4. Tokenizar el texto en oraciones (sin eliminar stopwords)
def tokenizar_oraciones(texto):
    oraciones = sent_tokenize(texto)
    return oraciones


# 5. Traducir el texto al inglés
def traducir_a_ingles(texto):
    if not texto.strip():
        return ""  # Retornar cadena vacía si el texto está vacío
    try:
        return translator.translate(texto)
    except Exception as e:
        print(f"Error en la traducción: {e}")
        return texto  # Si hay un error, devolver el texto original


# 6. Análisis de emociones con NRCLex
def analizar_emociones_nrc(texto):
    if not texto.strip():
        return {}  # Retornar diccionario vacío si el texto está vacío
    emociones = NRCLex(texto)
    return emociones.raw_emotion_scores  # Devuelve un diccionario con las emociones detectadas


# 7. Determinar la emoción predominante según el análisis de NRCLex
def emocion_predominante(emociones):
    if emociones:
        return max(emociones, key=emociones.get)
    else:
        return "neutral"


# Ejemplo completo del proceso:
def analizar_texto(texto):
    # Traducir el texto al inglés
    texto_ingles = traducir_a_ingles(texto)

    if not texto_ingles.strip():
        return {"error": "El texto no es válido o está vacío."}

    # Tokenizar y limpiar el texto en palabras
    tokens = tokenizar_texto(texto_ingles)
    tokens_sin_stopwords = eliminar_stopwords_en(tokens)  # Eliminamos stopwords en inglés

    # Tokenizar el texto en oraciones (sin eliminar stopwords)
    oraciones = tokenizar_oraciones(texto_ingles)

    # Análisis de emociones para palabras
    emociones_palabras = analizar_emociones_nrc(' '.join(tokens_sin_stopwords))
    emocion_predominante_palabras = emocion_predominante(emociones_palabras)

    # Análisis de emociones para bigramas
    bigramas = list(ngrams(tokens_sin_stopwords, 2))
    bigramas_como_texto = [' '.join(bigrama) for bigrama in bigramas]
    emociones_bigramas = analizar_emociones_nrc(' '.join(bigramas_como_texto))
    emocion_predominante_bigramas = emocion_predominante(emociones_bigramas)

    # Análisis de emociones para oraciones
    emociones_oraciones = analizar_emociones_nrc(' '.join(oraciones))
    emocion_predominante_oraciones = emocion_predominante(emociones_oraciones)

    # Consenso de emociones
    if (emocion_predominante_palabras == emocion_predominante_bigramas == emocion_predominante_oraciones):
        emociones = {
            emocion_predominante_palabras: '100%'
        }
    else:
        # Si no coinciden, calculamos el consenso con pesos
        emociones = {
            emocion_predominante_palabras: '20%',
            emocion_predominante_bigramas: '30%',
            emocion_predominante_oraciones: '50%'
        }

    return emociones