# Conectar el MCP a Copilot Studio

Archivos para registrar el MCP como **Custom Connector** en Power Platform y consumirlo desde **Copilot Studio**.

## Archivos

- `mcp-connector-swagger.json` — Definición OpenAPI 2.0 del custom connector. Apunta al endpoint SSE del MCP en Azure Container Apps.

## Pasos para importar

1. Entrar a [Power Apps Maker Portal](https://make.powerapps.com) y seleccionar el *Environment* correcto.
2. Menú lateral → *More → Discover all → Custom connectors*.
3. *+ Nuevo conector personalizado → Importar un archivo de OpenAPI*.
4. Subir `mcp-connector-swagger.json` y darle un nombre (ej. `MCP Synapse Analytics`).
5. En la solapa *Security*: dejar **No authentication** para una primera prueba (luego endurecer).
6. En *Definition* verificar que la operación `InvokeMCP` apunta a `GET /sse` y conserva la extensión `x-ms-agentic-protocol: mcp-sse`.
7. *Create connector*.
8. *Test → New connection → Test operation*.

## Usar en Copilot Studio

1. [Copilot Studio](https://copilotstudio.microsoft.com) → abrir/crear el Agent.
2. *Tools → Add a tool → Model Context Protocol*.
3. Elegir el connector recién creado, crear la *Connection*.
4. Activar las tools que se descubren automáticamente desde el MCP.

## Notas

- El `host` apunta al Container App público:
  `containerappmcpv2.delightfulground-71e1552d.eastus2.azurecontainerapps.io`.
- Las tools del MCP están definidas en `server.py` con el decorador `@mcp.tool()` y se descubren automáticamente vía protocolo MCP. **No** hay que listarlas en este Swagger.
- Si en el futuro se cambia el FQDN del Container App, actualizar el campo `host` y reimportar el connector.
