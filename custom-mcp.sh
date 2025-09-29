docker run -d --name mcp-gateway \
  -v "$(pwd)/../mcp_config.yml:/app/mcp_config.yml" \
  -e CEREBRAS_API_KEY="YOUR_CEREBRAS_API_KEY" \
  -p 8080:8080 \
  my-mcp-gateway:local
