from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os
from dotenv import load_dotenv

# Add the project root to the python path
sys.path.append(os.getcwd())
load_dotenv()

from config.config import settings

def get_latest_notification():
    # Convert async URL to sync URL
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        print(f"DB URL (masked): {db_url.split('@')[-1] if '@' in db_url else db_url}")
        
        # Check Notificacion count
        count = session.execute(text("SELECT count(*) FROM notificacion")).scalar()
        print(f"Total Notificaciones: {count}")

        # Check latest Notificacion
        sql = text("SELECT notificacion_id, titulo, mensaje, severidad_codigo, estado_codigo, metadata, creado FROM notificacion ORDER BY creado DESC LIMIT 1;")
        result = session.execute(sql).fetchone()
        
        if result:
            print(f"\n--- Última Notificación ---")
            print(f"ID: {result[0]}")
            print(f"Título: {result[1]}")
            print(f"Mensaje: {result[2]}")
            print(f"Severidad: {result[3]}")
            print(f"Estado: {result[4]}")
            print(f"Metadata: {result[5]}")
            print(f"Creado: {result[6]}")
            print("-" * 30)
        else:
            print("No se encontraron notificaciones.")

        # Check PerfilRiesgo
        print("\n--- Verificando Perfil Riesgo created ---")
        perfil = session.execute(text("SELECT nombre_normalizado, creado FROM perfil_riesgo WHERE nombre_normalizado LIKE '%FRONTLINE%'")).fetchone()
        if perfil:
            print(f"Perfil encontrado: {perfil[0]} created at {perfil[1]}")
        else:
            print("Perfil 'FRONTLINE' no encontrado.")
            
    except Exception as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    get_latest_notification()
