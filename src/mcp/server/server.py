import os
import re
import sys
import traceback
from typing import List, Any, Dict, Union, Optional
try:
    import pyodbc
except ImportError:
    pyodbc = None
from pydantic import BaseModel
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("MSSQL Tools Service")

# ------------------ Models ------------------

class QueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]

class ExecResult(BaseModel):
    message: str
    affected_rows: int

# ------------------ DB Helpers ------------------

def get_connection():
    if pyodbc is None:
        raise ImportError("pyodbc is not installed. Install it with: pip install pyodbc")
    try:
        conn_str = (
            f"DRIVER={{{os.environ.get('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={os.environ.get('MSSQL_SERVER')},{os.environ.get('MSSQL_PORT', '1433')};"
            f"DATABASE={os.environ.get('MSSQL_DATABASE')};"
            f"UID={os.environ.get('MSSQL_USER')};"
            f"PWD={os.environ.get('MSSQL_PASSWORD')}"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"❌ DB connection error: {e}", file=sys.stderr)
        raise

def validate_table_name(name: str) -> str:
    if not re.match(r'^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)?$', name):
        raise ValueError(f"Invalid table name: {name}")
    return f"[{name.replace('.', '].[')}]"

# ------------------ Tools ------------------

@mcp.tool()
def list_tables() -> Dict[str, List[str]]:
    """List all base tables in the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            return {"tables": [row[0] for row in cursor.fetchall()]}
    except Exception as e:
        print("❌ list_tables error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"tables": []}

@mcp.tool()
def preview_table(table_name: str) -> Dict[str, Any]:
    """Preview first 100 rows of a table."""
    try:
        safe_name = validate_table_name(table_name)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 100 * FROM {safe_name}")
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = [list(row) for row in cursor.fetchall()]
            return {"columns": columns, "rows": rows}
    except Exception as e:
        print(f"❌ preview_table error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"columns": [], "rows": []}

@mcp.tool()
def run_query(query: str) -> Union[Dict[str, Any], Dict[str, str]]:
    """Run any SQL query (SELECT/INSERT/UPDATE/DELETE)."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return QueryResult(columns=columns, rows=rows).model_dump()
            else:
                conn.commit()
                return ExecResult(message="Query executed successfully", affected_rows=cursor.rowcount).model_dump()
    except Exception as e:
        print("❌ run_query error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def describe_table(table_name: str) -> Dict[str, Any]:
    """Get detailed schema information for a specific table."""
    try:
        safe_name = validate_table_name(table_name)
        with get_connection() as conn:
            cursor = conn.cursor()
            table_only = table_name.split('.')[-1]
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """, table_only)
            columns = cursor.fetchall()
            return {
                "table_name": table_name,
                "columns": [{
                    "name": str(col[0]) if col[0] else "",
                    "type": str(col[1]) if col[1] else "",
                    "nullable": str(col[2]) == "YES" if col[2] else False,
                    "default": str(col[3]) if col[3] else None,
                    "max_length": int(col[4]) if col[4] else None
                } for col in columns]
            }
    except Exception as e:
        print(f"❌ describe_table error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_table_count(table_name: str) -> Dict[str, Any]:
    """Get the total row count for a table."""
    try:
        safe_name = validate_table_name(table_name)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {safe_name}")
            result = cursor.fetchone()
            count = int(result[0]) if result and result[0] is not None else 0
            return {"table_name": table_name, "row_count": count}
    except Exception as e:
        print(f"❌ get_table_count error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e)}

# ------------------ Run Server ------------------

if __name__ == "__main__":
    print("🚀 Starting MSSQL MCP Server on HTTP/SSE", file=sys.stderr)
    print("📋 Available tools:", file=sys.stderr)
    print("   • list_tables() - List all tables in database", file=sys.stderr)
    print("   • preview_table(table_name) - Preview first 100 rows", file=sys.stderr)
    print("   • describe_table(table_name) - Get table schema", file=sys.stderr)
    print("   • get_table_count(table_name) - Get row count", file=sys.stderr)
    print("   • run_query(query) - Execute any SQL query", file=sys.stderr)
    mcp.run(transport="sse")