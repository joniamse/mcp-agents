import os
import pyodbc
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.routing import Route
from starlette.responses import JSONResponse
from agents.compras import buscar_solped_oc, buscar_por_comprador, buscar_solpeds_pendientes

# DNS rebinding protection del SDK MCP se auto-activa cuando el host es
# localhost y rechaza requests con Host headers distintos a 127.0.0.1/localhost.
# Detrás del ingress HTTPS de Azure Container Apps la deshabilitamos para que
# acepte el Host header de *.azurecontainerapps.io.
mcp = FastMCP(
    "synapse-analytics-agent",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

SQL_CONFIG = os.getenv("SQL_CONNECTION_STRING")

@mcp.tool()
def tool_buscar_solped_oc(numero: str) -> str:
    """Busca una SolPed o Una Orden de Compra por número."""
    return buscar_solped_oc(numero, connection_string=SQL_CONFIG)

@mcp.tool()
def tool_buscar_por_comprador(comprador: str) -> str:
    """Busca OCs por usuario SAP (ej: TCERRI)."""
    return buscar_por_comprador(comprador, connection_string=SQL_CONFIG)

@mcp.tool()
def tool_solpeds_pendientes(centro: str = None) -> str:
    """Devuelve Solpeds sin OC asignada."""
    return buscar_solpeds_pendientes(centro, connection_string=SQL_CONFIG)

@mcp.tool()
def ping() -> str:
    """Verifica que el servidor MCP está activo"""
    return "MCP Server activo OK"

async def health(request):
    return JSONResponse({"status": "ok", "server": "MCP Agents"})

async def health_db(request):
    if not SQL_CONFIG:
        return JSONResponse({
            "status": "error",
            "detalle": "Variable SQL_CONNECTION_STRING no configurada"
        }, status_code=500)
    try:
        conn = pyodbc.connect(SQL_CONFIG, timeout=20)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return JSONResponse({
            "status": "ok",
            "detalle": "Conexión a SQL Server exitoso"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "detalle": str(e)
        }, status_code=500)

app = mcp.sse_app()
app.routes.append(Route("/ping", health))
app.routes.append(Route("/ping-db", health_db))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
