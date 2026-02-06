
from app.core.domain.guia_aerea import GuiaAerea
from app.core.repository.manifiesto_repository import ManifiestoRepository
from app.core.domain.manifiesto import Manifiesto
from dto.trama_dtos import TramaFiltroRequest
from dto.trama_dtos import ManifiestoFiltroRequest
from dto.trama_dtos import ManifiestoResponse
from app.core.repository.guia_aerea_filtro_repository import GuiaAereaFiltroRepository
from core.service.service_base import ServiceBase
from app.core.services.trama_service import TramaService
from typing import List
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from utl.constantes import Constantes

class TramaServiceImpl(TramaService, ServiceBase):
    
     def __init__(self, guia_aerea_filtro_repository:GuiaAereaFiltroRepository, manifiesto_repository: ManifiestoRepository ):
        self.guia_aerea_filtro_repository = guia_aerea_filtro_repository
        self.manifiesto_repository = manifiesto_repository

     async def findTramas(self, t: ManifiestoFiltroRequest) -> tuple[List[ManifiestoResponse], int]:
          filters = []
          filters.append(Manifiesto.habilitado == Constantes.HABILITADO)

          if t.numeroVuelo:
               filters.append(Manifiesto.numero_vuelo.ilike(f"%{t.numeroVuelo.upper()}%"))
          if t.fechaInicioVuelo:
               filters.append(Manifiesto.fecha_vuelo >= t.fechaInicioVuelo)
          if t.fechaFinVuelo:
               filters.append(Manifiesto.fecha_vuelo <= t.fechaFinVuelo)
          if t.aerolineaCodigo:
               filters.append(Manifiesto.aerolinea_codigo.ilike(f"%{t.aerolineaCodigo.upper()}%"))
          if t.estadoCodigo:
               filters.append(Manifiesto.estado_codigo == t.estadoCodigo)
          
          data, total_count = await self.manifiesto_repository.find(
            filters=filters,
            start=t.start,
            limit=t.limit,
            sort=t.sort
          )
          return data, total_count

     async def find(self, request: TramaFiltroRequest) -> tuple[List[GuiaAereaDataGrid], int]:
          filters = []
        
          filters.append(GuiaAereaDataGrid.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.PROCESADO)
          filters.append(GuiaAereaDataGrid.habilitado == Constantes.HABILITADO)

          if request.numeroVuelo:
               filters.append(GuiaAereaDataGrid.numero_vuelo.ilike(f"%{request.numeroVuelo.upper()}%"))
        
          if request.aerolineaCodigo:
               filters.append(GuiaAereaDataGrid.aerolinea_codigo.ilike(f"%{request.aerolineaCodigo.upper()}%"))

          if request.fechaInicioVuelo:
               filters.append(GuiaAereaDataGrid.fecha_consulta >= request.fechaInicioVuelo)
          if request.fechaFinVuelo:
               filters.append(GuiaAereaDataGrid.fecha_consulta <= request.fechaFinVuelo)
             

          
          data, total_count = await self.guia_aerea_filtro_repository.find_data_grid(
            filters=filters,
            start=request.start,
            limit=request.limit,
            sort=request.sort
          )
          return data, total_count

     async def get_records_by_manifiesto_ids(self, ids: List[str]) -> List[GuiaAereaDataGrid]:
          guia_ids = []
          for mid in ids:
               manifiesto = await self.manifiesto_repository.get_with_guias(mid)
               if manifiesto and manifiesto.guias:
                    guia_ids.extend([str(g.guia_aerea_id) for g in manifiesto.guias])
          
          if not guia_ids:
              return []
              
          return await self.guia_aerea_filtro_repository.find_by_ids(guia_ids)

     async def validate_batch(self, guias: List[GuiaAereaDataGrid]) -> dict:
          errors = []
          warnings = []

          if not guias:
               return {"status": "ERROR", "messages": ["No se han seleccionado guías."], "resumen": {}}

          # 1. Validar Vuelos Únicos
          vuelos = set(g.numero_vuelo for g in guias if g.numero_vuelo)
          if len(vuelos) > 1:
               warnings.append(f"Mezcla de vuelos: {', '.join(vuelos)}. Se recomienda generar tramas por vuelo único.")
          
          # 2. Validar Pesos
          peso_total = sum(g.peso_bruto or 0 for g in guias)
          if peso_total <= 0:
               errors.append("El peso total es 0.00. Verifique los pesos de las guías.")

          # 3. Validar Piezas
          piezas_total = sum(g.cantidad_piezas or 0 for g in guias)
          if piezas_total <= 0:
                errors.append("La cantidad total de piezas es 0.")

          # 4. Validar Aerolinea (Carrier ID)
          carriers = set(g.aerolinea_codigo for g in guias if g.aerolinea_codigo)
          for c in carriers:
              if len(c) not in [2, 3]:
                  errors.append(f"Código de aerolínea inválido: '{c}'. Debe tener 2 o 3 caracteres (Ej. MU).")

          status = "OK"
          if errors:
               status = "ERROR"
          elif warnings:
               status = "WARNING"
          
          return {
               "status": status,
               "messages": errors + warnings,
               "resumen": {
                    "total_guias": len(guias),
                    "peso_total": float(peso_total),
                    "piezas_total": piezas_total
               }
          }

     def generate_flat_file_content(self, guias: List[GuiaAereaDataGrid]) -> str:
          lines = []
          if not guias: return ""
          
          # Header FFM
          # Format: FFM/Version/Flight/Date/Route
          first = guias[0]
          vuelo = first.numero_vuelo or "UNKNOWN"
          # Simple date formatting for FFM
          fecha = first.fecha_vuelo.strftime('%d%b').upper() if hasattr(first, 'fecha_vuelo') and first.fecha_vuelo else "NOW"
          origen = first.origen_codigo or "LIM"
          
          lines.append(f"FFM/8/{vuelo}/{fecha}/{origen}")
          
          for g in guias:
               # FWB Line simulation: FWB/AWB/ORIGDEST/PCS/KG/VOL/DESC
               awb = g.numero.replace("-", "") if g.numero else "00000000000"
               org = g.origen_codigo or ""
               dst = g.destino_codigo or ""
               pcs = g.cantidad_piezas or 0
               wgt = g.peso_bruto or 0.0
               vol = g.volumen or 0.0
               desc = (g.descripcion_mercancia or "CONSOL").upper()[:15]
               
               lines.append(f"FWB/{awb}/{org}{dst}/{pcs}/{wgt}/{vol}/{desc}")
               
          return "\n".join(lines)


     def _determine_operation_type(self, origen: str, destino: str) -> str:
          aeropuertos_peru = ['LIM', 'CUZ', 'IQT', 'PCL, AQP', 'TCQ', 'JUL', 'PEM']
          
          is_origin_peru = origen in aeropuertos_peru
          is_dest_peru = destino in aeropuertos_peru
          
          if not is_origin_peru and is_dest_peru:
               return "INGRESO"
          elif is_origin_peru and not is_dest_peru:
               return "SALIDA"
          else:
               return "NACIONAL / OTRO"

     async def get_data_grid_records_by_ids(self, ids: List[str]) -> List[GuiaAereaDataGrid]:
          return await self.guia_aerea_filtro_repository.find_by_ids(ids)

     async def get_data_grid_records_by_manifiesto_id(self, manifiesto_id: str) -> List[GuiaAereaDataGrid]:
          return await self.guia_aerea_filtro_repository.find_by_manifiesto_id(manifiesto_id)

     async def generate_manifest_pdf(self, guias: List[GuiaAereaDataGrid]) -> bytes:
          try:
               import fitz  # PyMuPDF
               from io import BytesIO
               doc = fitz.open()
               page = doc.new_page(width=595, height=842) # A4
               
               if not guias:
                    page.insert_text((50, 50), "Sin guias para mostrar", fontsize=12)
                    return BytesIO(doc.tobytes())

               # Extract Manifest Data from first guide's relation if available, or use defaults
               first = guias[0]
               # Attempt to get manifiesto object if loaded, otherwise fallback
               # Safe check to avoid MissingGreenlet if lazy loading is triggered in async context
               manifiesto = first.__dict__.get('manifiesto')
               
               tvuelo = first.numero_vuelo or "---"
               tfecha = "---"
               taerolinea = "---"
               torigen = first.origen_codigo or "LIM"
               tdestino = first.destino_codigo or "LIM"
               
               if manifiesto:
                    tvuelo = manifiesto.numero_vuelo or tvuelo
                    # Format Date with Year
                    if manifiesto.fecha_vuelo:
                        tfecha = manifiesto.fecha_vuelo.strftime('%d/%m/%Y').upper()
                    taerolinea = manifiesto.aerolinea_codigo or "---"
                    
                    # Try to get route from manifesto if it had one, but manifesto usually has specific ports?
                    # Actually manifesto just links guias. We can infer route from the first guia.
                    if manifiesto.origen_codigo: torigen = manifiesto.origen_codigo
                    if manifiesto.destino_codigo: tdestino = manifiesto.destino_codigo
                    
               elif first.fecha_vuelo:
                    tfecha = first.fecha_vuelo.strftime('%d/%m/%Y').upper()
                    taerolinea = first.aerolinea_codigo or "---"

               # Determine Operation Type
               tipo_operacion = self._determine_operation_type(torigen, tdestino)

               # -- HEADER --
               y = 40
               # Title
               page.insert_text((200, y), f"MANIFIESTO DE CARGA - {tipo_operacion}", fontsize=14, fontname="Helvetica-Bold")
               y += 20
               page.insert_text((230, y), "(BORRADOR)", fontsize=10, fontname="Helvetica-Oblique", color=(0.5, 0.5, 0.5))
               y += 30

               # Header Grid
               # Left
               page.insert_text((50, y), f"ADUANA: 118 - AEREA DEL CALLAO", fontsize=10)
               y += 15
               page.insert_text((50, y), f"AÑO: {tfecha.split('/')[-1] if '/' in tfecha else '---'}", fontsize=10)
               y += 15
               page.insert_text((50, y), f"CARRIER ID: {taerolinea}", fontsize=10)
               
               y -= 30 # Back up
               # Right
               page.insert_text((350, y), f"VUELO: {tvuelo}", fontsize=10)
               y += 15
               page.insert_text((350, y), f"FECHA ARRIBO: {tfecha}", fontsize=10)
               y += 15
               page.insert_text((350, y), f"TIPO OPERACIÓN: {tipo_operacion}", fontsize=10)
               
               y += 30
               page.draw_line((50, y), (550, y))
               y += 10

               # -- COLUMNS --
               # Define columns: AWB, CONSIGNATARIO, ORIG/DEST, BULTOS, PESO(KG), VOL(CBM), NATURALEZA
               headers = [
                   ("GUIA AEREA", 50), 
                   ("CONSIGNATARIO / RUC", 130), 
                   ("RUTA", 280), 
                   ("BULTOS", 330), 
                   ("PESO (KG)", 380), 
                   ("VOL (CBM)", 440), 
                   ("NATURALEZA", 500)
               ]
               
               for title, x in headers:
                   page.insert_text((x, y), title, fontsize=8, fontname="Helvetica-Bold")
               
               y += 10
               page.draw_line((50, y), (550, y))
               y += 15
               
               # -- ROWS --
               total_pcs = 0
               total_wgt = 0.0
               total_vol = 0.0
               
               for g in guias:
                    # Data Prep
                    awb = g.numero or ""
                    
                    # Consignee & RUC
                    cons_name = "---"
                    cons_ruc = "---"
                    
                    # Find Consignee in intervinientes
                    if hasattr(g, 'intervinientes') and g.intervinientes:
                         # Filter logic could be better if we had specific code constants
                         # Assuming standard codes or simple loop
                         for inter in g.intervinientes:
                              # Check common codes for Consignee
                              if str(inter.rol_codigo).upper() in ['CNE', 'CONSIGNATARIO']:
                                   cons_name = (inter.nombre or "")[:20]
                                   cons_ruc = inter.numero_documento or "No registrado"
                                   break
                    
                    # Fallback to older fields if relationship empty/failed
                    if cons_name == "---" and hasattr(g, 'nombre_consignatario'):
                         cons_name = (g.nombre_consignatario or "")[:20]
                    
                    if cons_ruc == "---":
                        cons_ruc = "No registrado"

                    ruta = f"{g.origen_codigo}-{g.destino_codigo}"
                    
                    pcs = g.cantidad_piezas or 0
                    pkg_type = "CT" # Defaulting to CT (Cartons) for MVP if not present
                    
                    wgt = float(g.peso_bruto or 0)
                    vol = float(g.volumen or 0)
                    
                    nat_desc = (g.naturaleza_carga_codigo or "---")
                    
                    # Totals
                    total_pcs += pcs
                    total_wgt += wgt
                    total_vol += vol
                    
                    # Draw Row
                    fontsize = 8
                    
                    page.insert_text((headers[0][1], y), awb, fontsize=fontsize)
                    
                    # Multi-line for Consignee
                    page.insert_text((headers[1][1], y), cons_name, fontsize=fontsize)
                    page.insert_text((headers[1][1], y+10), f"RUC: {cons_ruc}", fontsize=7, color=(0.4, 0.4, 0.4))
                    
                    page.insert_text((headers[2][1], y), ruta, fontsize=fontsize)
                    
                    page.insert_text((headers[3][1], y), f"{pcs} {pkg_type}", fontsize=fontsize)
                    
                    page.insert_text((headers[4][1], y), f"{wgt:,.2f}", fontsize=fontsize)
                    page.insert_text((headers[5][1], y), f"{vol:,.3f}", fontsize=fontsize)
                    
                    page.insert_text((headers[6][1], y), nat_desc[:12], fontsize=fontsize)

                    y += 25 # Increased row height for multi-line
                    
                    if y > 750:
                         page = doc.new_page(width=595, height=842)
                         y = 50
               
               y += 10
               page.draw_line((50, y), (550, y))
               y += 20
               
               # -- TOTALS --
               page.insert_text((50, y), f"TOTALES:", fontsize=10, fontname="Helvetica-Bold")
               page.insert_text((330, y), f"{total_pcs}", fontsize=10, fontname="Helvetica-Bold")
               page.insert_text((380, y), f"{total_wgt:,.2f}", fontsize=10, fontname="Helvetica-Bold")
               page.insert_text((440, y), f"{total_vol:,.3f}", fontsize=10, fontname="Helvetica-Bold")
               
               y += 40
               page.insert_text((50, y), f"ID TRANSMISIÓN SUNAT: ________________________ (PENDIENTE)", fontsize=10)
               
               buffer = BytesIO(doc.tobytes())
               return buffer
          except ImportError:
               from io import BytesIO
               return BytesIO(b"Error: PyMuPDF not installed.")

     async def generate_manifest_xml(self, guias: List[GuiaAerea]) -> str:
          """
          Generates XML content based on SUNAT OMA v3.7 standard.
          """
          import xml.etree.ElementTree as ET
          from xml.dom import minidom
          from datetime import datetime

          if not guias:
               return ""

          # Namespaces
          NS_DEC = "urn:wco:datamodel:WCO:DEC-DMS:2"
          NS_RAM = "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:103"
          
          ET.register_namespace('', NS_DEC)
          ET.register_namespace('ram', NS_RAM)

          # Root Element: Declaration
          root = ET.Element(f"{{{NS_DEC}}}Declaration")
          
          # --- HEADER DATA ---
          first = guias[0]
          manifiesto = first.__dict__.get('manifiesto')
          
          tvuelo = first.numero_vuelo or "UNKNOWN"
          tfecha = datetime.now()
          taerolinea = first.aerolinea_codigo or "UNKNOWN"
          torigen = first.origen_codigo or "LIM"
          tdestino = first.destino_codigo or "LIM"

          if manifiesto:
               tvuelo = manifiesto.numero_vuelo or tvuelo
               if manifiesto.fecha_vuelo: tfecha = manifiesto.fecha_vuelo
               taerolinea = manifiesto.aerolinea_codigo or taerolinea
               if manifiesto.origen_codigo: torigen = manifiesto.origen_codigo
               if manifiesto.destino_codigo: tdestino = manifiesto.destino_codigo
          elif first.fecha_vuelo:
               tfecha = first.fecha_vuelo

          op_type_code = "0401" if self._determine_operation_type(torigen, tdestino) == "INGRESO" else "0402"

          # 1. FunctionCode (9 = Original)
          func_code = ET.SubElement(root, f"{{{NS_DEC}}}FunctionCode")
          func_code.text = "9"

          # 2. WCODataModelVersionCode
          wco_ver = ET.SubElement(root, f"{{{NS_DEC}}}WCODataModelVersionCode")
          wco_ver.text = "3.7"

          # 3. DeclarationOffice (118 = Callao)
          decl_office = ET.SubElement(root, f"{{{NS_DEC}}}DeclarationOffice")
          decl_office_id = ET.SubElement(decl_office, f"{{{NS_DEC}}}ID")
          decl_office_id.text = "118"

          # 4. ID (Transmission ID) - Logic: Carrier-Flight-Date
          decl_id = ET.SubElement(root, f"{{{NS_DEC}}}ID")
          decl_id.text = f"{taerolinea}-{tvuelo}-{tfecha.strftime('%Y%m%d')}"
          
          # 5. SpecifiedTransactionID
          spec_txn = ET.SubElement(root, f"{{{NS_RAM}}}SpecifiedTransactionID")
          spec_txn_id = ET.SubElement(spec_txn, f"{{{NS_RAM}}}ID")
          spec_txn_id.text = op_type_code

          # 6. BorderTransportMeans (Flight Info)
          border_transport = ET.SubElement(root, f"{{{NS_DEC}}}BorderTransportMeans")
          journey_id = ET.SubElement(border_transport, f"{{{NS_RAM}}}JourneyID")
          journey_id.text = tvuelo
          
          # Arrival Date
          arrival_dt = ET.SubElement(border_transport, f"{{{NS_RAM}}}ActualArrivalDateTime") 
          arrival_dt.set("formatCode", "204") 
          arrival_dt.text = tfecha.strftime("%Y%m%d") + "000000"

          # --- CONSIGNMENTS ---
          for g in guias:
               consignment = ET.SubElement(root, f"{{{NS_DEC}}}Consignment")
               
               clean_awb = (g.numero or "").replace("-", "").replace(" ", "")
               cid = ET.SubElement(consignment, f"{{{NS_DEC}}}ID")
               cid.text = clean_awb
               
               # Consignee
               cons_name = "PARTICULAR"
               cons_ruc = "00000000000"
               cons_address = "LIMA, PERU"
               cons_country = "PE"
               cons_doc_type = "6" # Default RUC

               if hasattr(g, 'intervinientes') and g.intervinientes:
                    for inter in g.intervinientes:
                         if str(inter.rol_codigo).upper() in ['CNE', 'CONSIGNATARIO']:
                              cons_name = (inter.nombre or "PARTICULAR")
                              cons_ruc = (inter.numero_documento or "00000000000")
                              # Address composition 
                              parts = []
                              if inter.direccion: parts.append(inter.direccion)
                              if inter.ciudad: parts.append(inter.ciudad)
                              cons_address = ", ".join(parts) if parts else "LIMA, PERU"
                              cons_country = (inter.pais_codigo or "PE")
                              
                              # Determine Doc Type
                              if len(cons_ruc) == 11: cons_doc_type = "6" # RUC
                              elif len(cons_ruc) == 8: cons_doc_type = "1" # DNI
                              else: cons_doc_type = "4" # Carnet Ext / Passport (Fallback)
                              break
               
               if cons_name == "PARTICULAR" and hasattr(g, 'nombre_consignatario') and g.nombre_consignatario:
                    cons_name = g.nombre_consignatario

               cne_node = ET.SubElement(consignment, f"{{{NS_DEC}}}Consignee")
               
               # ID with schemeID (Catalog 27)
               cne_id = ET.SubElement(cne_node, f"{{{NS_DEC}}}ID")
               cne_id.set("schemeID", cons_doc_type)
               cne_id.text = cons_ruc

               cne_name = ET.SubElement(cne_node, f"{{{NS_DEC}}}Name")
               cne_name.text = cons_name
               
               cne_addr = ET.SubElement(cne_node, f"{{{NS_DEC}}}Address")
               addr_line = ET.SubElement(cne_addr, f"{{{NS_DEC}}}Line")
               addr_line.text = cons_address
               country_code = ET.SubElement(cne_addr, f"{{{NS_DEC}}}CountryCode")
               country_code.text = cons_country
               
               # Package
               total_pkg = ET.SubElement(consignment, f"{{{NS_DEC}}}TotalPackageQuantity")
               total_pkg.text = str(g.cantidad_piezas or 0)
               
               # Weight
               gross_wgt = ET.SubElement(consignment, f"{{{NS_DEC}}}TotalGrossMassMeasure") # OMA uses TotalGrossMassMeasure usually
               gross_wgt.set("unitCode", "KGM")
               gross_wgt.text = f"{float(g.peso_bruto or 0):.3f}"
               
               # Volume
               if g.volumen and float(g.volumen) > 0:
                    vol_node = ET.SubElement(consignment, f"{{{NS_DEC}}}GrossVolumeMeasure")
                    vol_node.set("unitCode", "MTQ") 
                    vol_node.text = f"{float(g.volumen):.3f}"
                    
               # Description
               desc_text = (g.naturaleza_carga_codigo or g.descripcion_mercancia or "CONSOLIDATED" )[:100]
               desc = ET.SubElement(consignment, f"{{{NS_DEC}}}CargoDescription")
               desc.text = desc_text

          # Return pretty printed XML
          rough_string = ET.tostring(root, 'utf-8')
          reparsed = minidom.parseString(rough_string)
          return reparsed.toprettyxml(indent="  ")


     