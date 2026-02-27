import asyncio
import asyncpg
import json

async def run_query():
    # Connect directly with asyncpg
    conn = await asyncpg.connect('postgresql://postgres.jinyomztyfhqrjwglyyb:Tivit2025..@aws-1-sa-east-1.pooler.supabase.com:6543/postgres')
    
    # Run the query logic similar to find_dispersion_by_perfil
    perfil_id = 'c484dd0b-ce59-46c8-bac2-60f8f19f97a7'
    perfil = await conn.fetchrow("SELECT nombre_normalizado, variaciones_nombre, tipo_interviniente_codigo FROM perfil_riesgo WHERE perfil_riesgo_id = $1", perfil_id)
    
    if not perfil:
        print("Perfil not found")
        await conn.close()
        return

    print("Perfil:", dict(perfil))
    
    var_raw = perfil['variaciones_nombre']
    if var_raw and isinstance(var_raw, str):
      variaciones = json.loads(var_raw) 
    else:
      variaciones = var_raw if var_raw else []

    nombres = set(variaciones)
    if perfil['nombre_normalizado']:
        nombres.add(perfil['nombre_normalizado'])
    nombres_list = list(nombres)
    
    print("Nombres a buscar:", nombres_list)
    
    result = await conn.fetch("""
        SELECT g.fecha_emision, g.peso_bruto, i.nombre
        FROM guia_aerea_interviniente i
        JOIN guia_aerea1 g ON i.guia_aerea_id = g.guia_aerea_id
        WHERE i.nombre = ANY($1::varchar[])
        AND i.rol_codigo = $2
        AND g.peso_bruto IS NOT NULL
        AND g.fecha_emision IS NOT NULL
        ORDER BY g.fecha_emision
    """, nombres_list, perfil['tipo_interviniente_codigo'])
    
    print(f"Encontrados: {len(result)} guias")
    for r in result:
        print(dict(r))
        
    await conn.close()

asyncio.run(run_query())
