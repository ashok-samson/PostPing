# 🐘 PostPing

A lightweight FastAPI app that lets you test PostgreSQL connectivity using either traditional credentials or Azure Managed Identity. It provides a simple web UI to log messages, view stored entries, and validate connection status.

---

## 🚀 Features

- ✅ Checks PostgreSQL connectivity on load (with error feedback)
- 📝 Add log entries with timestamp
- 📋 View all logs in a clean table
- ❌ Delete individual log entries
- 🔐 Supports Azure Managed Identity or connection string auth

---

## ⚙️ Configuration

Set the following environment variables based on your preferred authentication mode:

### Option 1: Traditional Credentials
```env
USE_MANAGED_IDENTITY=false
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
```

### Option 2: Managed Identity (Azure)
```env
USE_MANAGED_IDENTITY=true
DB_HOST=<your-server>.postgres.database.azure.com
DB_NAME=<your-database-name>
DB_USER=<identity-user>@<tenant-id>
```

> ✅ Recommended: Store these in an `.env` file locally or configure them in Azure App Service environment settings.

---

## 🐳 Docker Support

Build and run the app locally with Docker:

```bash
docker build -t postping .
docker run -e USE_MANAGED_IDENTITY=false -e DATABASE_URL=... -p 8000:8000 postping
```

Or use Managed Identity:

```bash
docker run -e USE_MANAGED_IDENTITY=true -e DB_HOST=... -e DB_NAME=... -e DB_USER=... -p 8000:8000 postping
```

---

## 🌐 Accessing the App

Once running:
```
http://localhost:8000
```

---

## 📦 Dependencies (see `requirements.txt`)
- fastapi
- uvicorn
- sqlalchemy
- psycopg2-binary
- jinja2
- python-dotenv
- azure-identity *(for managed identity support)*

---

## 📄 License
MIT License

---

## 💬 Name Meaning
**PostPing** — A simple tool to ping your PostgreSQL setup, log messages, and validate connectivity.

---

Feel free to customize this app to fit into your diagnostics or DevOps toolbelt! 🚀

