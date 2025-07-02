# MSSQL MCP Server

A Model Context Protocol (MCP) server for Microsoft SQL Server database operations.

## Features

- **List Tables**: Get all base tables in the database
- **Preview Table**: View first 100 rows of any table
- **Run Query**: Execute any SQL query (SELECT/INSERT/UPDATE/DELETE)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your MSSQL connection details
```

3. Run the server:
```bash
python server.py
```

## Environment Variables

- `MSSQL_SERVER`: SQL Server hostname/IP
- `MSSQL_PORT`: SQL Server port (default: 1433)
- `MSSQL_DATABASE`: Database name
- `MSSQL_USER`: Username
- `MSSQL_PASSWORD`: Password
- `MSSQL_DRIVER`: ODBC driver (default: ODBC Driver 17 for SQL Server)

## Tools

### list_tables()
Returns all base tables in the database.

### preview_table(table_name: str)
Shows first 100 rows of the specified table.

### run_query(query: str)
Executes any SQL query and returns results or execution status.

## Transport

The server supports SSE (Server-Sent Events) and StreamableHTTP transports.