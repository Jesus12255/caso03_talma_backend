from datetime import (
    datetime,
    date,
    time,
    timedelta
)
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import List
import calendar
import locale

# Locale español Perú
try:
    locale.setlocale(locale.LC_TIME, "es_PE.UTF-8")
except:
    pass  # Windows puede no tenerlo instalado

TIME_ZONE = ZoneInfo("America/Bogota")

ISO_FRONT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

TIME_FORMAT = "%H:%M:%S.%f"
TIME_FORMAT_03 = "%H:%M"
TIME_FORMAT_01 = "%I:%M"
TIME_FORMAT_02 = "%p"

FORMAT01 = "%d de %B de %Y"
FORMAT02 = "%Y%m%d%H%M%S"
FORMAT03 = "%Y%m%d"
FORMATO_REPORTE = "%d/%m/%Y"
FORMATO_DATE_TIME = "%d/%m/%Y %H:%M"
FORMATO_DATE_TIME_AP = "%d/%m/%Y %H:%M %p"
FORMAT_DATE = "%d-%m-%Y"
RENIEC_FORMAT = "%Y%m%d"
MIGRACIONES_FORMAT = "%d/%m/%Y"


class DateUtil:

    @staticmethod
    def format_date(fecha: date, fmt: str) -> str:
        return fecha.strftime(fmt) if fecha else ""

    @staticmethod
    def format_datetime(fecha: datetime, fmt: str) -> str:
        return fecha.strftime(fmt) if fecha else ""

    @staticmethod
    def current_date_as_string() -> str:
        return datetime.now(ZoneInfo("America/Lima")).strftime(FORMAT01)

    @staticmethod
    def get_current_local_date() -> date:
        return datetime.now(TIME_ZONE).date()

    @staticmethod
    def get_current_local_datetime() -> datetime:
        return datetime.now(TIME_ZONE)

    @staticmethod
    def get_current_year() -> int:
        return datetime.now(TIME_ZONE).year

    @staticmethod
    def get_current_month() -> int:
        return datetime.now(TIME_ZONE).month

    @staticmethod
    def get_current_day() -> int:
        return datetime.now(TIME_ZONE).day

    @staticmethod
    def get_current_hour() -> int:
        return datetime.now(TIME_ZONE).hour

    @staticmethod
    def get_current_minute() -> int:
        return datetime.now(TIME_ZONE).minute

    @staticmethod
    def get_current_second() -> int:
        return datetime.now(TIME_ZONE).second

    @staticmethod
    def get_current_millisecond() -> int:
        return int(datetime.now(TIME_ZONE).timestamp() * 1000)

    @staticmethod
    def get_cantidad_dias(inicio: date, fin: date) -> int:
        return (fin - inicio).days if inicio and fin else 0

    @staticmethod
    def get_cantidad_anios(inicio: date, fin: date) -> Decimal:
        return Decimal(fin.year - inicio.year) if inicio and fin else Decimal(0)

    @staticmethod
    def get_cantidad_meses(inicio: date, fin: date) -> Decimal | None:
        if not inicio or not fin:
            return None
        return Decimal((fin.year - inicio.year) * 12 + fin.month - inicio.month)

    @staticmethod
    def add_days_datetime(fecha: datetime, days: int) -> datetime:
        return fecha + timedelta(days=days)

    @staticmethod
    def get_nombre_mes(mes: int) -> str:
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return meses.get(mes, "")

    @staticmethod
    def get_abreviatura_mes(mes: int) -> str:
        abrevs = {
            1: "EN", 2: "FEB", 3: "MAR", 4: "ABR",
            5: "MAY", 6: "JUN", 7: "JUL", 8: "AG",
            9: "SET", 10: "OCT", 11: "NOV", 12: "DIC"
        }
        return abrevs.get(mes, "")

    @staticmethod
    def to_local_date(fecha: str) -> date | None:
        if not fecha:
            return None
        return datetime.strptime(fecha, ISO_FRONT_FORMAT).date()

    @staticmethod
    def of_date(fecha: str, fmt: str) -> date | None:
        if not fecha:
            return None
        return datetime.strptime(fecha, fmt).date()

    @staticmethod
    def of_datetime(fecha: str, fmt: str) -> datetime | None:
        if not fecha:
            return None
        return datetime.strptime(fecha, fmt)

    @staticmethod
    def is_today_sunday() -> bool:
        return datetime.now().weekday() == 6

    @staticmethod
    def get_dias_hasta_sabado(fecha: datetime) -> int:
        dia_actual = fecha.weekday()
        if dia_actual == 5 and fecha.time() < time(6, 0):
            return 0
        return (5 - dia_actual) % 7

    @staticmethod
    def get_nombre_dia(fecha: datetime) -> str:
        return f"{fecha.day:02d}"

    @staticmethod
    def get_etiquetas_horas_del_dia() -> List[str]:
        ahora = datetime.now()
        hora_final = ahora.hour + 1
        etiquetas = []
        for h in range(hora_final + 1):
            etiquetas.append("23:59" if h == 23 else f"{h:02d}:00")
        return etiquetas

    @staticmethod
    def convertir_hora_a_24_horas(entrada: str) -> str:
        try:
            entrada = entrada.replace("\u00A0", " ").strip()
            partes = entrada.split()
            hora_12 = " ".join(partes[1:5])
            hora_12 = hora_12.replace("p. m.", "PM").replace("a. m.", "AM")
            fecha = datetime.strptime(hora_12, "%d/%m/%Y %I:%M:%S %p")
            return fecha.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return "Formato inválido"
