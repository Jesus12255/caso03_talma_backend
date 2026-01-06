class Constantes:
    BLANK_SPACE = " "
    SYSTEM_USER = "SYSTEM"
    VALIDATE_MANUAL_CONFIDENCE = 1
    VALID_FILE_FORMATS = {
        '.pdf':  {'mime': {'application/pdf'}, 'magic': b'%PDF'},
        '.jpg':  {'mime': {'image/jpeg'}, 'magic': b'\xFF\xD8\xFF'},
        '.jpeg': {'mime': {'image/jpeg'}, 'magic': b'\xFF\xD8\xFF'},
        '.png':  {'mime': {'image/png'}, 'magic': b'\x89PNG\r\n\x1a\n'},
        '.docx': {'mime': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}, 'magic': b'PK\x03\x04'},
        '.xlsx': {'mime': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'}, 'magic': b'PK\x03\x04'},
        '.doc':  {'mime': {'application/msword'}, 'magic': b'\xD0\xCF\x11\xE0'},
        '.xls':  {'mime': {'application/vnd.ms-excel'}, 'magic': b'\xD0\xCF\x11\xE0'},
    }
    GUION = "-"
    SLASH = "/"

    UUID_NULL = None
    TRUE = "true"
    HABILITADO = True
    INHABILITADO = False
    CERO = "0"

    PAGINATION_START = 0
    PAGINATION_SIZE = 20

    MAXIMO_CARGA_INSPECCIONES = 200
    MINIMO_IMAGEN_SEGUIMIENTO = 1

    EMPTY = ""
    CSC = "CSC-PERU"
    SUCCESS = "success"

    SCHEMA = "public"
    CATALOG = "sigma_db"

    SI = True
    NO = False

    FILE_NAME_BLOB = "blob"

    MAX_CANT_OBSERVACIONES = 3
    LONGUITUD_CODIGO_CATALOGO = 3

    ACCESS = "ACCESS"

    SMS_INICIO = 100000
    SMS_FIN = 999999

    TDC_SOLICITUD = "VARIOS"

    NUMERO_SIN_MEDIDOR = 0

    SI_TXT = "SI"
    NO_TXT = "NO"
    NA_TXT = "NO APLICA"

    MAX_FILE_SIZE = 10 * 1024 * 1024
    MAX_FILE_SIZE_TEXT = "10MB"

    ZONA_CODIGO = "Z"
    NIVEL_CODIGO = "N"


    class PesoCampoGuiaAerea:
        # =========================
        # Identificación del documento
        # =========================
        NUMERO = 0.12
        FECHA_EMISION = 0.05
        ESTADO_GUIA_CODIGO = 0.03

        # =========================
        # Ruta y transporte
        # =========================
        ORIGEN_CODIGO = 0.04
        DESTINO_CODIGO = 0.04
        TRANSBORDO = 0.02
        AEROLINEA_CODIGO = 0.03
        NUMERO_VUELO = 0.02
        FECHA_VUELO = 0.02

        # =========================
        # Mercancía
        # =========================
        DESCRIPCION_MERCANCIA = 0.06
        CANTIDAD_PIEZAS = 0.04
        PESO_BRUTO = 0.04
        PESO_COBRADO = 0.03
        UNIDAD_PESO_CODIGO = 0.01
        VOLUMEN = 0.01
        NATURALEZA_CARGA_CODIGO = 0.01

        # =========================
        # Costos y valores
        # =========================
        VALOR_DECLARADO = 0.06
        TIPO_FLETE_CODIGO = 0.03
        TARIFA_FLETE = 0.03
        OTROS_CARGOS = 0.02
        MONEDA_CODIGO = 0.03
        TOTAL_FLETE = 0.03

        # =========================
        # Intervinientes – Remitente
        # =========================
        REMITENTE_NOMBRE = 0.03
        REMITENTE_NUMERO_DOCUMENTO = 0.03
        REMITENTE_PAIS_CODIGO = 0.02
        REMITENTE_DIRECCION = 0.01
        REMITENTE_CIUDAD = 0.005
        REMITENTE_TELEFONO = 0.005

        # =========================
        # Intervinientes – Consignatario
        # =========================
        CONSIGNATARIO_NOMBRE = 0.03
        CONSIGNATARIO_NUMERO_DOCUMENTO = 0.03
        CONSIGNATARIO_PAIS_CODIGO = 0.02
        CONSIGNATARIO_DIRECCION = 0.01
        CONSIGNATARIO_CIUDAD = 0.005
        CONSIGNATARIO_TELEFONO = 0.005

        # =========================
        # Metadatos / control
        # =========================
        INSTRUCCIONES_ESPECIALES = 0.02
        OBSERVACIONES = 0.01


    class EstadoRegistroGuiaAereea: 
        PROCESANDO = "ESTGA001"
        OBSERVADO = "ESTGA002"
        PROCESADO = "ESTGA003"
        ENVIADO = "ESTGA004"
        ACEPTADO = "ESTGA005"
        RECHAZADO = "ESTGA006"
        
    
    class TipoGuiaAerea:
        MAESTRA = "TPGA001"
        HIJA = "TPGA002"
    
    class EstadoConfianza: 
        AUTO_VALIDADO = "ESTCO001"
        REVISION_MANUAL = "ESTCO002"
        
    class TipoInterviniente:
        REMITENTE = "TPIN001"
        CONSIGNATARIO = "TPIN002"
       

    class Vista:
        GUIA_AEREA_REGISTROS = "VC001"
        GUIA_AEREA_REGISTROS_SUBSANAR = "VC002"

class Catalogo:
    VALORES_CONSTANTES = "VALORES_CONSTANTES"
    ESTADO_USUARIO = "ESTADO_USUARIO"
    TIPO_DOCUMENTO = "TIPO_DOCUMENTO"
    SEXO = "SEXO"
    PRIORIDAD = "PRIORIDAD"
    MEDICO = "MEDICO"
    TIPO_INSPECCION = "TIPO_INSPECCION"
    CONECTADO = "CONECTADO"
    ESTADO = "ESTADO_EQUIPO"
    FUNCIONA = "FUNCIONA"
    TIPO_SENALIZACION = "TIPO_SENALIZACION"
    ESTADO_CAPACITACION = "ESTADO_CAPACITACION"
    TIPO_CAPACITACION = "TIPO_CAPACITACION"
    ESTADO_EXTINTOR = "ESTADO_EXTINTOR"
    TIPO_CAPACIDAD = "TIPO_CAPACIDAD"
    TIPO_EXTINTOR = "TIPO_EXTINTOR"
    PABELLON = "PABELLON"
    GRADO_ESTUDIOS = "GRADO_ESTUDIOS"
    TIPO_SANGRE = "TIPO_SANGRE"
    TIPO_ALTERNATIVA = "TIPO_ALTERNATIVA"

    def __init__(self):
        raise RuntimeError("Catalogo is a constants-only class")


