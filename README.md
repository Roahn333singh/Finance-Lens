

# 💰 Finance-Lens

**Finance-Lens** is a local **Finance Tracker built with MCP (Model Context Protocol)**.  
It lets you record, view, and summarize your daily expenses using structured MCP tools — designed to integrate seamlessly with MCP-compatible clients such as ChatGPT or Claude Desktop.

---

## 🚀 Features

- 📥 **Add Expenses** — record transactions with date, amount, and category  
- 📊 **List Expenses** — view expenses within a given date range  
- 📈 **Summarize** — get aggregated spending data by category  
- 🗑️ **Delete Expenses** — remove specific entries by ID  
- 🗂️ **Categories Resource** — fetches expense categories from a local JSON file  
- 💾 **Local SQLite Storage** — automatically creates and manages your database  
- ⚡ **MCP Server Integration** — can run locally via `stdio` for ChatGPT / Claude  

---

## ⚙️ Installation

### 1️⃣ Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended Python package manager)
- [FastMCP](https://pypi.org/project/fastmcp/)
- [aiosqlite](https://pypi.org/project/aiosqlite/)

### 2️⃣ Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/Finance-Lens.git
cd Finance-Lens

# Install dependencies
uv sync
```
## Edit your MCP config.json file
```bash
{
  "mcpServers": {
    "Finance-Lens": {
      "command": "<User uv path>",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "<main.py file path>"
      ],
      "cwd": "<Project Directory path>",
      "env": {},
      "transport": "stdio",
      "type": "mcp"
    }
  }
}

