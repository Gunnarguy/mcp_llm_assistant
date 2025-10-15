# MCP Server Architecture - Critical Understanding

## What I Was Missing

The MCP (Model Context Protocol) specification defines **THREE** types of server capabilities:

### 1. Tools (What We're Using)
- **Functions** that the LLM can invoke
- Example: `API-post-search`, `API-get-block-children`, `API-retrieve-a-database`
- Notion MCP server exposes **19 tools** (all API endpoints)
- Accessed via: `docker mcp tools call <TOOL_NAME> '<JSON_ARGS>'`

### 2. Resources (What We're NOT Using)
- **Context/data** that can be listed and subscribed to
- Example: Individual files, documents, database records exposed as URIs
- Notion MCP server **does NOT expose resources** - only tools
- Would be accessed via: `resources/list` and `resources/read` (if implemented)

### 3. Prompts (What We're NOT Using)
- **Templated prompts** with parameters
- Example: Pre-built prompt templates for common tasks
- Notion MCP server **does NOT expose prompts**
- Would be accessed via: `prompts/list` and `prompts/get` (if implemented)

## The Root Problem

**What I thought:** Notion exposes each page/database as a resource that can be listed and filtered.

**Reality:** Notion only exposes API endpoints as tools. To find content, you must:
1. Call `API-post-search` (returns flat list of pages/databases)
2. Parse results to find parent page ID
3. Call `API-get-block-children` with page ID to get nested blocks
4. Look for `child_database` blocks in the response
5. Call `API-retrieve-a-database` for each database to get full details

## Notion's Hierarchical Structure

```
Workspace
├── Page: "Our Mission to Autonomy"
│   ├── Block: Heading
│   ├── Block: Paragraph
│   ├── Block: child_database (Database 1)
│   ├── Block: child_database (Database 2)
│   └── Block: child_database (Database 3)
├── Page: "Another Page"
└── Database: "Top-level Database"
```

**Key Insight:** `API-post-search` returns the root level pages/databases, but NOT nested child databases. You must traverse the tree.

## Correct Discovery Workflow

### To find "all databases within Our Mission to Autonomy":

```bash
# Step 1: Search for the parent page
docker mcp tools call API-post-search

# Step 2: Parse JSON output, find page with title "Our Mission to Autonomy", extract ID
# Example: page_id = "1478f5ab-d5f4-813f-b85d-f0c9a1916996"

# Step 3: Get child blocks
docker mcp tools call API-get-block-children '{"block_id":"1478f5ab-d5f4-813f-b85d-f0c9a1916996"}'

# Step 4: Parse results for "child_database" type blocks, extract database IDs

# Step 5: For each database, get full details
docker mcp tools call API-retrieve-a-database '{"database_id":"<DB_ID>"}'
```

## Why This Matters

**Before:** The system prompt said "just call API-post-search and filter results"
- This only works for TOP-LEVEL databases
- Misses any databases nested inside pages
- Leads to incomplete results (user said "there are at least 4 databases" - we only found 2)

**After:** The system prompt now explains:
- Notion's hierarchical structure
- The need to traverse: search → get page → get children → get database
- How to use `API-get-block-children` to discover nested content

## Official MCP Specification References

### Protocol Messages for Tools
- `tools/list` - Discover available tools (what we're using to see 19 Notion tools)
- `tools/call` - Invoke a tool (what we're doing with `docker mcp tools call`)

### Protocol Messages for Resources (Not Used by Notion)
- `resources/list` - List available resources (URIs)
- `resources/read` - Read resource content by URI
- `resources/subscribe` - Subscribe to resource updates

### Protocol Messages for Prompts (Not Used by Notion)
- `prompts/list` - List available prompt templates
- `prompts/get` - Get prompt template with arguments

## Docker MCP Gateway CLI

The `docker mcp` CLI provides access to MCP servers via:

```bash
# List servers
docker mcp server list

# List tools from a server
docker mcp tools list <SERVER_NAME>

# Call a tool
docker mcp tools call <TOOL_NAME> '<JSON_ARGS>'

# Inspect server capabilities
docker mcp server inspect <SERVER_NAME>
```

**Note:** There is NO `docker mcp resources` or `docker mcp prompts` because the gateway only implements tool calls (as most MCP servers only expose tools).

## The Fix Applied

Updated `app/services/llm_service.py` system prompt to:
1. Explain Notion's hierarchical structure
2. Provide step-by-step workflow for discovering nested databases
3. Emphasize the need to call `API-get-block-children` when users ask for content "within" a page

## Testing the Fix

Try asking: **"list all databases within Our Mission to Autonomy"**

Expected behavior:
1. LLM calls `API-post-search`
2. LLM parses results to find "Our Mission to Autonomy" page_id
3. LLM calls `API-get-block-children` with that page_id
4. LLM identifies child_database blocks
5. LLM calls `API-retrieve-a-database` for each database
6. LLM returns complete list of all databases (should find 4+)

## References

- Official MCP Spec: https://spec.modelcontextprotocol.io/specification/2025-06-18/
- Tools Specification: https://spec.modelcontextprotocol.io/specification/2025-06-18/server/tools/
- Resources Specification: https://spec.modelcontextprotocol.io/specification/2025-06-18/server/resources/
- Notion MCP Server: https://github.com/makenotion/notion-mcp-server
