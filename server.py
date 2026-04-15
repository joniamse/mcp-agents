import os
from mcp.server.fastmcp import FastMCP
from agents.compras import buscar_solped_oc, buscar_por_comprador, buscar_solpeds_pendientes

mcp = FastMCP("synapse-analytics-agent")

SQL_CONFIG = os.getenv("SQL_CONNECTION_STRING")

@mcp.tool()
def tool_buscar_solped_oc(numero: str) -> str:
    """
    Busca una SolPed o Una Orden de Compra por número.
    Acepta números de 6 u 8 dígitos, con o sin ceros a la izquierda.
    Busca en las columnas Solped_Nro y OC_Nro.
    """
    return buscar_solped_oc(numero)

@mcp.tool()
def tool_buscar_por_comprador(comprador: str) -> str:
    """
    Busca todas las Órdenes de Compra gestionadas por un comprador específico.
    El parámetro comprador es el nombre de usuario SAP, por ejemplo: TCERRI, PCORAZZA.
    """
    return buscar_por_comprador(comprador)

@mcp.tool()
def tool_solpeds_pendientes(centro: str = None) -> str:
    """
    Devuelve las Solpeds que aún no tienen una OC asignada.
    Opcionalmente se puede filtrar por nombre de centro: RASA, HB4, SYN, RIPA, BIOSEM, SEMYA, RIBRA.
    """
    return buscar_solpeds_pendientes(centro)

@mcp.tool()
def ping() -> str:
    """Verifica que el servidor MCP está activo"""
    return "MCP Server activo OK"

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=8000, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
