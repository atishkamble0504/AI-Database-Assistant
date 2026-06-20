# AI Database Assistant

An AI-powered SQLite Database Assistant that allows users to interact with databases using natural language. Instead of writing SQL manually, users can ask questions in plain English, and the application automatically generates, validates, executes, and explains SQL queries.

## Features

* Natural Language → SQL conversion using AI
* SQLite database support
* Upload custom `.db` files
* Automatic SQL error correction
* Query explanation in simple English
* Dangerous query detection and confirmation system
* Smart suggestions when no matching data is found
* Export query results to:

  * CSV
  * JSON
  * Excel (XLSX)
* Export complete database to:

  * JSON
  * Excel
* Conversation-aware query generation
* Web-based interface built with Flask

---

## Project Architecture

```text
User Question
      │
      ▼
Flask Web Interface
      │
      ▼
AI SQL Generator
      │
      ▼
Generated SQL
      │
      ▼
Safety Validation Layer
      │
      ▼
SQLite Database
      │
      ▼
Results + Explanation
      │
      ▼
Export (CSV / JSON / Excel)
```

---

## Tech Stack

* Python
* Flask
* SQLite
* OpenAI SDK
* OpenRouter API
* OpenPyXL
* HTML / CSS

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/atishkamble0504/AI-Database-Assistant.git
cd AI-Database-Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openrouter_api_key
FLASK_SECRET_KEY=your_secret_key
```

---

## Run Application

```bash
python ui.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## Example Queries

```text
Show all employees
```

```text
List customers from Germany
```

```text
How many products are in the database?
```

```text
Create a new table named departments
```

```text
Delete all inactive users
```

---

## Security Features

* API keys stored in environment variables
* Dangerous SQL operation warnings
* Confirmation required before destructive actions
* Uploaded database isolation
* Automatic cleanup of uploaded databases
* No secrets stored in source code

---

## Export Options

### Query Results

* CSV
* JSON
* Excel

### Entire Database

* JSON
* Excel

### Individual Tables

* CSV

---

## Project Structure

```text
AI-Database-Assistant/
│
├── main.py
├── ui.py
├── create_db.py
├── .env.example
├── .gitignore
├── LICENSE
│
└── templates/
    └── index.html
```

---

## Future Improvements

* Support for MySQL and PostgreSQL
* User authentication
* Query history persistence
* Interactive charts and dashboards
* Multi-database management
* AI-generated database insights

---

## License

This project is licensed under the MIT License.

---

## Author

**Atish Kamble**

GitHub: https://github.com/atishkamble0504
