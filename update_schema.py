from sqlalchemy import create_engine, text
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Construct sync DB URL from env or hardcode from config (assuming knowing the pattern)
# It's better to read from config, but config likely has async driver.
# Let's try to replace 'postgresql+asyncpg' with 'postgresql+psycopg2' if present in env, 
# or just hardcode passing the connection string manually or importing config and modifying it.

from config.config import settings

def update_schema():
    # Convert async URL to sync URL for this script
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    
    logger.info(f"Connecting to DB to update schema...")
    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            logger.info("Deep breath... altering table...")
            # We need to drop the index if it exists because it depends on dimension
            # But maybe we just alter type and let it fail/succeed.
            # pgvector: "You canâ€™t alter the dimensions of a vector column if it has an index"
            # So first drop index if exists.
            
            # 1. Drop index (safe if not exists)
            # connection.execute(text("DROP INDEX IF EXISTS embedding_idx;")) # Assuming name
            
            # 2. Alter column type
            # Using USING clause to zero-pad or truncate is possible but complicated.
            # Since this is dev environment, we can just clear the column or Drop/Add if needed.
            # Or assume ALTER TYPE works (it fails if data exists with different dim)
            
            # Let's try ALTER TYPE with explicit casting if failure occurs. 
            # Actually, standard ALTER TYPE vector(3072) might fail if data exists.
            # "cannot alter type of column "vector_identidad" because it is used in index" is possible.
            
            # Let's just try to ALTER. If fails, we might need to truncate column.
            sql = text("ALTER TABLE perfil_riesgo ALTER COLUMN vector_identidad TYPE vector(3072);")
            connection.execute(sql)
            connection.commit()
            logger.info("Schema updated successfully: vector_identidad is now vector(3072)")
            
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
        logger.info("If error is about mismatch length of data, you might need to TRUNCATE the column first:")
        logger.info("UPDATE perfil_riesgo SET vector_identidad = NULL;")

if __name__ == "__main__":
    update_schema()
