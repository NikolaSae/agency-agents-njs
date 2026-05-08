# Example MCP Server

This is a sample MCP (Model Context Protocol) server built with FastMCP in Python, optimized for deployment on Azure Container Apps.

## Overview

This server provides three example tools:
- **search_issues**: Searches GitHub issues in a repository
- **get_weather**: Fetches current weather data for a location
- **calculate_expression**: Safely evaluates mathematical expressions

## Technology Recommendation

For MCP servers, we recommend **Azure Container Apps + FastMCP** over Azure Functions MCP Extension because:

- **Better Developer Experience**: FastMCP provides a dedicated framework with automatic Pydantic validation and tool registration
- **Performance**: Container Apps have lower cold start times compared to Functions for containerized workloads
- **Flexibility**: Full control over the runtime environment and dependencies
- **Scalability**: Serverless auto-scaling with Container Apps
- **Ecosystem Integration**: Seamless integration with Azure services and monitoring

Azure Functions would require building a custom MCP extension and dealing with HTTP transport complexities, while Container Apps allow running the MCP server as-is with stdio transport.

## Project Structure

```
mcp-server-example/
├── main.py              # Main server code with tool definitions
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container build configuration
├── README.md           # This file
└── .env                # Environment variables (not committed)
```

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```

## Tool Examples

### search_issues
```python
# Example usage
result = await search_issues(repo="microsoft/vscode", state="open", limit=5)
# Returns JSON array of issues with number, title, author, state
```

### get_weather
```python
# Example usage
result = await get_weather(location="New York")
# Returns: "Weather in New York: Partly cloudy, Temperature: 22°C, Feels like: 25°C"
```

### calculate_expression
```python
# Example usage
result = await calculate_expression(expression="2 * (3 + 4) / 2")
# Returns: "Result: 7.0"
```

## Deployment to Azure Container Apps

1. **Build and push Docker image**:
   ```bash
   docker build -t your-registry.azurecr.io/mcp-server:latest .
   docker push your-registry.azurecr.io/mcp-server:latest
   ```

2. **Create Container App**:
   ```bash
   az containerapp create \
     --name mcp-server \
     --resource-group your-rg \
     --image your-registry.azurecr.io/mcp-server:latest \
     --env-vars GITHUB_TOKEN=your-token \
     --target-port 8000 \
     --ingress external
   ```

3. **Configure MCP client** to connect to the Container App endpoint.

## Security Notes

- Store API keys in Azure Key Vault and reference them as environment variables
- Use managed identity for Azure service authentication
- Implement proper error handling and input validation
- Consider rate limiting for public-facing tools

## Troubleshooting

- **Import errors**: Ensure all dependencies are installed
- **API failures**: Check environment variables and network connectivity
- **Container issues**: Verify Dockerfile and Azure Container Registry access