from io import BytesIO
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid

class PDFService:
    
    def generate_manifest(self, guias: List[GuiaAereaDataGrid]) -> BytesIO:
        buffer = BytesIO()
        # Landscape for more columns
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4),
            rightMargin=30, leftMargin=30, 
            topMargin=30, bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # 1. Header
        # Group by Flight if possible, otherwise use the first one or generic header
        vuelo = "MÚLTIPLES"
        fecha = "-"
        if guias:
            vuelo = f"{guias[0].aerolinea_codigo or ''} {guias[0].numero_vuelo or ''}" 
            fecha = str(guias[0].fecha_vuelo) if guias[0].fecha_vuelo else "-"
            
        header_text = f"MANIFIESTO DE CARGA - {vuelo} / {fecha}"
        title = Paragraph(header_text, styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5 * cm))
        
        # 2. Table Data
        # Columns: AWB, Origen, Destino, Piezas, Peso, Shipper, Consignee, Desc
        headers = ["AWB", "Org", "Dst", "Pcs", "Peso (Kg)", "Embarcador", "Consignatario", "Descripción"]
        
        data = [headers]
        
        total_pieces = 0
        total_weight = 0.0
        
        for g in guias:
            # Use DataGrid fields directly
            shipper = (g.nombre_remitente or "-")[:35] # Expanded truncated length
            consignee = (g.nombre_consignatario or "-")[:35]
            
            # If RUC/ID is needed, DataGrid needs those columns or we concatenate
            # Current DataGrid has address/phone/city/country for sender/consignee but maybe not ID/RUC explicitly?
            # It maps 'remitente_gai_id' but not 'numero_documento_remitente'.
            # We will use just names as requested.

            pieces = g.cantidad_piezas or 0
            weight = float(g.peso_bruto or 0.0)
            
            total_pieces += pieces
            total_weight += weight
            
            row = [
                g.numero,
                g.origen_codigo,
                g.destino_codigo,
                str(pieces),
                f"{weight:.2f}",
                shipper, 
                consignee, 
                (g.descripcion_mercancia or "")[:30] # Truncate
            ]
            data.append(row)
            
        # 3. Table Style
        table = Table(data, colWidths=[
            1.5*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.8*inch, 
            2.0*inch, 2.0*inch, 2.5*inch
        ])
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (5, 1), (7, -1), 'LEFT'), # Align names left
        ])
        table.setStyle(style)
        elements.append(table)
        
        elements.append(Spacer(1, 0.5 * cm))
        
        # 4. Totals
        totals_text = f"<b>TOTAL PIEZAS:</b> {total_pieces}   |   <b>TOTAL PESO:</b> {total_weight:.2f} Kg"
        elements.append(Paragraph(totals_text, styles['Normal']))
        
        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer
