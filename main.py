from fastmcp import FastMCP
import os
import aiosqlite
import sqlite3
import json

# ----------------------------------------------------------------------
# ✅ 1. Use a persistent, user-local path for the database
# ----------------------------------------------------------------------
DB_DIR = os.path.expanduser("~/.finance_lens")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "expenses.db")

# Categories JSON (optional)
CATEGORIES_PATH = os.path.join(DB_DIR, "categories.json")

print(f"✅ Using persistent database at: {DB_PATH}")

# ----------------------------------------------------------------------
# ✅ 2. Initialize database once (sync, safe)
# ----------------------------------------------------------------------
def init_db():
    try:
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
            c.commit()
            print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Initialize immediately at module load
init_db()

# ----------------------------------------------------------------------
# ✅ 3. Initialize FastMCP app
# ----------------------------------------------------------------------
mcp = FastMCP("Finance-Lens")

# ----------------------------------------------------------------------
# ✅ 4. MCP Tools
# ----------------------------------------------------------------------

@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                """
                INSERT INTO expenses(date, amount, category, subcategory, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (date, amount, category, subcategory, note)
            )
            await c.commit()
            expense_id = cur.lastrowid
            return {
                "status": "success",
                "id": expense_id,
                "message": f"Expense added successfully (ID {expense_id})"
            }
    except Exception as e:
        if "readonly" in str(e).lower():
            return {
                "status": "error",
                "message": "Database is read-only. Check file permissions."
            }
        return {"status": "error", "message": f"Database error: {str(e)}"}


@mcp.tool()
async def list_expenses(start_date, end_date):
    """List expense entries within an inclusive date range."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                """
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (start_date, end_date)
            )
            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        return {"status": "error", "message": f"Error listing expenses: {str(e)}"}


@mcp.tool()
async def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            query = """
                SELECT category, SUM(amount) AS total_amount, COUNT(*) AS count
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY total_amount DESC"

            cur = await c.execute(query, params)
            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        return {"status": "error", "message": f"Error summarizing expenses: {str(e)}"}


@mcp.tool()
async def delete_expense(expense_id: int):
    """Delete an expense entry by its ID."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            await c.commit()
            if cur.rowcount > 0:
                return {"status": "success", "message": f"Expense {expense_id} deleted successfully"}
            else:
                return {"status": "error", "message": f"No expense found with ID {expense_id}"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting expense: {str(e)}"}


# ----------------------------------------------------------------------
# ✅ 5. Resource for categories
# ----------------------------------------------------------------------
@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    """Provide a JSON list of expense categories."""
    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other"
        ]
    }

    try:
        if os.path.exists(CATEGORIES_PATH):
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return f.read()
        else:
            with open(CATEGORIES_PATH, "w", encoding="utf-8") as f:
                json.dump(default_categories, f, indent=2)
            return json.dumps(default_categories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Could not load categories: {str(e)}"})


# ----------------------------------------------------------------------
# ✅ 6. Start MCP server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Run as a persistent HTTP server
    mcp.run(transport="http", host="0.0.0.0", port=2000)
