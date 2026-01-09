from typing import Any, Collection, Dict, Callable, TypeVar
from datetime import datetime
from utl.date_util import DateUtil, FORMAT02

import random
import base64
from threading import Lock

T = TypeVar("T")


class Constantes:
    EMPTY = ""
    CERO = "0"
    CSC = "CSC"
    TIPO_DOCUMENTO = "TIPO_DOCUMENTO"
    ROL = "ROL"




class GenericUtil:

    # =========================
    # NULOS
    # =========================
    @staticmethod
    def es_nulo(objeto: Any, atributo: str) -> bool:
        try:
            if isinstance(objeto, dict):
                val = objeto.get(atributo)
            else:
                val = getattr(objeto, atributo, None)
            return val is None
        except Exception:
            return True

    @staticmethod
    def no_es_nulo(objeto: Any, atributo: str) -> bool:
        try:
            if isinstance(objeto, dict):
                val = objeto.get(atributo)
            else:
                val = getattr(objeto, atributo, None)
            return val is not None
        except Exception:
            return False

    # =========================
    # EMPTY / NOT EMPTY
    # =========================
    @staticmethod
    def is_empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, (str, bytes)):
            return len(value) == 0
        if isinstance(value, (Collection, Dict)):
            return len(value) == 0
        return False

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        return not GenericUtil.is_empty(value)

    @staticmethod
    def is_empty_with_trim(value: str) -> bool:
        return value is None or value.strip() == Constantes.EMPTY

    @staticmethod
    def empty_if_string_null(value: str) -> str:
        return value if GenericUtil.is_not_empty(value) else Constantes.EMPTY

    @staticmethod
    def CSC_if_string_null(value: str) -> str:
        return value if GenericUtil.is_not_empty(value) else Constantes.CSC
    
    @staticmethod
    def is_empty_list(objeto: Any) -> bool:
        return isinstance(objeto, list) and GenericUtil.is_empty(objeto)
    
 

    # =========================
    # STRINGS
    # =========================
    @staticmethod
    def truncate(texto: str, longitud: int) -> str:
        return texto[:longitud]

    @staticmethod
    def replace_spaces(cadena: str) -> str:
        return cadena.replace(" ", "_") if cadena else None

    # =========================
    # FECHA / CODIGOS
    # =========================
    @staticmethod
    def build_code_8_unic() -> str:
        fecha = DateUtil.format_datetime(
            DateUtil.get_current_local_datetime(),
            FORMAT02
        )
        parte_fecha = fecha[-4:]
        numero_aleatorio = random.randint(1000, 9999)
        return f"{parte_fecha}{numero_aleatorio}"

    # =========================
    # NUMEROS
    # =========================
    @staticmethod
    def fill_zero(numero: int, longitud: int) -> str:
        return str(numero).zfill(longitud)

    @staticmethod
    def get_token() -> int:
        return random.randint(100000, 999999)

    @staticmethod
    def get_clave_sms(minimo: int, maximo: int) -> int:
        return random.randint(minimo, maximo)

    @staticmethod
    def fill_mensaje_error(index: int, mensaje: str) -> str:
        return f"{mensaje} -> fila: {index + 1}"

    # =========================
    # BASE64
    # =========================
    @staticmethod
    def decode_base64(base64_image: str) -> bytes | None:
        if GenericUtil.is_not_empty(base64_image):
            partes = base64_image.split(",")
            if len(partes) > 1:
                return base64.b64decode(partes[1])
        return None

    @staticmethod
    def to_base64(texto: str) -> str:
        return base64.b64encode(texto.encode()).decode()

    @staticmethod
    def get_byte_image(base64_string: str) -> str:
        if not GenericUtil.is_empty_with_trim(base64_string):
            return base64_string.split(",")[1]
        return Constantes.EMPTY

    # =========================
    # DISTINCT (STREAM JAVA)
    # =========================
    @staticmethod
    def distinct_by_key(key_extractor: Callable[[T], Any]):
        seen = set()
        lock = Lock()

        def predicate(item: T) -> bool:
            key = key_extractor(item)
            with lock:
                if key in seen:
                    return False
                seen.add(key)
                return True

        return predicate

    # =========================
    # REFLECTION (UPPERCASE)
    # =========================
    @staticmethod
    def to_upper_case(objeto: Any):
        for attr in vars(objeto):
            valor = getattr(objeto, attr)
            if isinstance(valor, str) and valor.strip():
                setattr(objeto, attr, valor.upper())


    @staticmethod
    def generate_unique_code_4() -> str:
        random_part = random.randint(1000, 9999)
        return f"{random_part}"