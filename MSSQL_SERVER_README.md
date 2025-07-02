# MSSQL MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Microsoft SQL Server databases.

## Features

- **list_tables()** - List all tables in the database
- **preview_table(table_name)** - Preview first 100 rows of a table
- **describe_table(table_name)** - Get detailed schema information
- **get_table_count(table_name)** - Get total row count for a table
- **run_query(query)** - Execute any SQL query (SELECT/INSERT/UPDATE/DELETE)

## Setup

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure database connection:**
   Edit the `.env` file with your database credentials:
   ```
   MSSQL_SERVER=your_server
   MSSQL_PORT=1433
   MSSQL_DATABASE=your_database
   MSSQL_USER=your_username
   MSSQL_PASSWORD=your_password
   MSSQL_DRIVER=ODBC Driver 17 for SQL Server
   ```

3. **Run the server:**
   ```bash
   python src/mcp/server/server.py
   ```

## Requirements

- Python 3.10+
- Microsoft ODBC Driver 17 for SQL Server
- Access to a SQL Server database

## Security Notes

- Always use parameterized queries when possible
- Ensure proper database permissions are set
- Keep your `.env` file secure and never commit it to version control

## Usage Examples

The server provides tools that can be called by MCP clients:

- List all tables: `list_tables()`
- Preview data: `preview_table("Users")`
- Get schema: `describe_table("Orders")`
- Count rows: `get_table_count("Products")`
- Run custom query: `run_query("SELECT TOP 10 * FROM Customers WHERE City = 'London'")`