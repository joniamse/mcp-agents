import pyodbc
import os

def get_connection():
    return pyodbc.connect(os.environ["DB_CONNECTION_STRING"])

def buscar_solped_oc(numero: str) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        numero_limpio = numero.strip().lstrip("0")

        query = """
            SELECT TOP 20
                Solped_Nro, Solped_Pos, Solped_Fecha, Solped_Status,
                OC_Nro, OC_Pos, OC_Fecha, OC_Comprador,
                Centro_Nombre, Sociedad, Grupo_Compras,
                Cod_Material, Descripcion_Material, Unidad_Medida,
                Solicitante_Original, Moneda_OC, Cantidad_Pedida,
                Precio_Unitario, Monto_Neto_OC, Monto_Neto_Moneda_Local,
                Origen_Flujo, Dias_Gestion, Semaforo_Eficiencia
            FROM dbo.TRAZABILIDAD_COMPRAS_TOTAL
            WHERE 
                RIGHT(LTRIM(RTRIM(Solped_Nro)), 6) LIKE ?
                OR RIGHT(LTRIM(RTRIM(OC_Nro)), 6) LIKE ?
        """

        cursor.execute(query, f"%{numero_limpio}%", f"%{numero_limpio}%")
        rows = cursor.fetchall()

        if not rows:
            return (
                f"No se encontraron registros para el número '{numero}'. "
                f"Verificá si el número es correcto o si corresponde a un ejercicio fiscal anterior."
            )

        resultados = []
        for row in rows:
            semaforo = {"Verde": "🟢", "Amarillo": "🟡", "Rojo": "🔴", "Gris": "⚫"}.get(row.Semaforo_Eficiencia, "")
            resultados.append(
                f"\n📋 Solped: {row.Solped_Nro or 'N/A'} | Pos: {row.Solped_Pos or 'N/A'} | "
                f"Fecha: {row.Solped_Fecha or 'N/A'} | Status: {row.Solped_Status or 'N/A'}\n"
                f"📦 OC: {row.OC_Nro or 'N/A'} | Pos: {row.OC_Pos or 'N/A'} | "
                f"Fecha: {row.OC_Fecha or 'N/A'} | Comprador: {row.OC_Comprador or 'N/A'}\n"
                f"🏭 Centro: {row.Centro_Nombre or 'N/A'} | Sociedad: {row.Sociedad or 'N/A'} | "
                f"Grupo Compras: {row.Grupo_Compras or 'N/A'}\n"
                f"🔩 Material: {row.Cod_Material or 'N/A'} - {row.Descripcion_Material or 'N/A'} "
                f"({row.Unidad_Medida or 'N/A'}) | Solicitante: {row.Solicitante_Original or 'N/A'}\n"
                f"💰 Moneda: {row.Moneda_OC or 'N/A'} | Cantidad: {row.Cantidad_Pedida or 'N/A'} | "
                f"Precio Unit.: {row.Precio_Unitario or 'N/A'} | Monto Neto: {row.Monto_Neto_OC or 'N/A'} | "
                f"Monto Local: {row.Monto_Neto_Moneda_Local or 'N/A'}\n"
                f"🔄 Origen: {row.Origen_Flujo or 'N/A'} | "
                f"Días Gestión: {row.Dias_Gestion or 'N/A'} | "
                f"Eficiencia: {semaforo} {row.Semaforo_Eficiencia or 'N/A'}"
            )

        return f"Se encontraron {len(rows)} registro(s):\n" + "\n---".join(resultados)

    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"


def buscar_por_comprador(comprador: str) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT TOP 50
                OC_Nro, Solped_Nro, OC_Fecha, Centro_Nombre,
                Descripcion_Material, Monto_Neto_OC, Moneda_OC,
                Origen_Flujo, Semaforo_Eficiencia
            FROM dbo.TRAZABILIDAD_COMPRAS_TOTAL
            WHERE OC_Comprador LIKE ?
            ORDER BY OC_Fecha DESC
        """

        cursor.execute(query, f"%{comprador.upper()}%")
        rows = cursor.fetchall()

        if not rows:
            return f"No se encontraron OCs para el comprador '{comprador}'."

        resultados = []
        for row in rows:
            semaforo = {"Verde": "🟢", "Amarillo": "🟡", "Rojo": "🔴", "Gris": "⚫"}.get(row.Semaforo_Eficiencia, "")
            resultados.append(
                f"OC: {row.OC_Nro or 'N/A'} | Solped: {row.Solped_Nro or 'N/A'} | "
                f"Fecha: {row.OC_Fecha or 'N/A'} | Centro: {row.Centro_Nombre or 'N/A'} | "
                f"Material: {row.Descripcion_Material or 'N/A'} | "
                f"Monto: {row.Monto_Neto_OC or 'N/A'} {row.Moneda_OC or ''} | "
                f"{semaforo} {row.Semaforo_Eficiencia or 'N/A'}"
            )

        return f"OCs del comprador '{comprador}' ({len(rows)} registros):\n" + "\n".join(resultados)

    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"


def buscar_solpeds_pendientes(centro: str = None) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT TOP 50
                Solped_Nro, Solped_Pos, Solped_Fecha, Solped_Status,
                Centro_Nombre, Grupo_Compras, Descripcion_Material,
                Solicitante_Original, Dias_Gestion
            FROM dbo.TRAZABILIDAD_COMPRAS_TOTAL
            WHERE Origen_Flujo = 'Solo Solped (Pendiente)'
        """

        if centro:
            query += " AND Centro_Nombre LIKE ?"
            query += " ORDER BY Solped_Fecha ASC"
            cursor.execute(query, f"%{centro.upper()}%")
        else:
            query += " ORDER BY Solped_Fecha ASC"
            cursor.execute(query)

        rows = cursor.fetchall()

        if not rows:
            return "No hay Solpeds pendientes de conversión a OC."

        resultados = []
        for row in rows:
            resultados.append(
                f"Solped: {row.Solped_Nro or 'N/A'} | Pos: {row.Solped_Pos or 'N/A'} | "
                f"Fecha: {row.Solped_Fecha or 'N/A'} | Status: {row.Solped_Status or 'N/A'} | "
                f"Centro: {row.Centro_Nombre or 'N/A'} | Grupo: {row.Grupo_Compras or 'N/A'} | "
                f"Material: {row.Descripcion_Material or 'N/A'} | "
                f"Solicitante: {row.Solicitante_Original or 'N/A'} | "
                f"Días sin gestión: {row.Dias_Gestion or 'N/A'}"
            )

        return f"Solpeds pendientes ({len(rows)} registros):\n" + "\n".join(resultados)

    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"