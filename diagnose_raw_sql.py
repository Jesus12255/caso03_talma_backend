
import asyncio
import asyncpg

DSN = "postgres://postgres.puikaqnvtnedsldtqbje:dAa24UoIfqw4MArs@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

async def diagnose():
    try:
        conn = await asyncpg.connect(DSN, statement_cache_size=0)
        print("Connected to DB.")
        
        rows = await conn.fetch("""
            SELECT guia_aerea_id, numero, estado_registro_codigo, numero_vuelo, fecha_vuelo, manifiesto_id 
            FROM guia_aerea1
            ORDER BY modificado DESC 
            LIMIT 5
        """)
        
        print(f"{'ID':<36} | {'Numero':<15} | {'Estado':<10} | {'Vuelo':<10} | {'Fecha Vuelo':<20} | {'Manifiesto ID'}")
        print("-" * 120)
        for row in rows:
            g_id = str(row['guia_aerea_id'])
            num = row['numero'] or "None"
            est = row['estado_registro_codigo'] or "None"
            vuelo = row['numero_vuelo'] or "None"
            fecha = str(row['fecha_vuelo']) if row['fecha_vuelo'] else "None"
            man = str(row['manifiesto_id']) if row['manifiesto_id'] else "None"
            
            print(f"{g_id} | {num:<15} | {est:<10} | {vuelo:<10} | {fecha:<20} | {man}")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
