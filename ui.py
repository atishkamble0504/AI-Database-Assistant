from flask import Flask, render_template, request, session, redirect, url_for, send_file
from main import (
    nl_to_sql, run_query, get_schema, resolve_db_path,
    result_to_csv, result_to_excel, result_to_json,
    export_db_excel, export_db_json, export_single_table_csv,
    get_all_tables
)
import os
import time
import io

app = Flask(__name__)
app.secret_key = "supersecret"

# -------------------------
# DOWNLOAD ORIGINAL DB
# -------------------------
@app.route("/download_db")
def download_db():
    db_path = session.get("db_path")

    if not db_path or not os.path.exists(db_path):
        return "❌ No active database to download"

    if "uploads" not in db_path:
        return "❌ Download allowed only for uploaded files"

    return send_file(
        db_path,
        as_attachment=True,
        download_name=os.path.basename(db_path)
    )

# =========================================================
# 🚀 EXPORT RESULT ROUTES
# =========================================================

@app.route("/export_result_csv")
def export_result_csv():
    index = int(request.args.get("index", 0))
    history = session.get("history", [])
    item = history[index] if index < len(history) else {}

    data = item.get("data", [])
    columns = item.get("columns", [])
    csv_data = result_to_csv(data, columns)

    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"result_{index}_{int(time.time())}.csv"
    )

@app.route("/export_result_json")
def export_result_json():
    index = int(request.args.get("index", 0))
    history = session.get("history", [])
    item = history[index] if index < len(history) else {}

    data = item.get("data", [])
    columns = item.get("columns", [])
    json_data = result_to_json(data, columns)

    return send_file(
        io.BytesIO(json_data.encode()),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"result_{index}_{int(time.time())}.json"
    )

@app.route("/export_result_excel")
def export_result_excel():
    index = int(request.args.get("index", 0))
    history = session.get("history", [])
    item = history[index] if index < len(history) else {}

    data = item.get("data", [])
    columns = item.get("columns", [])
    stream = result_to_excel(data, columns)

    return send_file(
        stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"result_{index}_{int(time.time())}.xlsx"
    )

# =========================================================
# 🚀 EXPORT FULL DATABASE
# =========================================================

@app.route("/export_db_excel")
def export_db_excel_route():
    db_path = session.get("db_path")
    stream = export_db_excel(db_path)
    return send_file(
        stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"database_{int(time.time())}.xlsx"
    )

@app.route("/export_db_json")
def export_db_json_route():
    db_path = session.get("db_path")
    json_data = export_db_json(db_path)
    return send_file(
        io.BytesIO(json_data.encode()),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"database_{int(time.time())}.json"
    )

@app.route("/export_db_csv")
def export_db_csv_route():
    db_path = session.get("db_path")
    table = request.args.get("table")
    if not table: return "❌ Table required"
    csv_data = export_single_table_csv(db_path, table)
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{table}_{int(time.time())}.csv"
    )

# =========================================================
# MAIN HANDLER
# =========================================================

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if "history" not in session:
        session["history"] = []

    if "conversation" not in session:
        session["conversation"] = []  # 🔥 NEW

    # -------------------------
    # SELECT / SWITCH DB
    # -------------------------
    if "select_db" in request.form:
        old_db_path = session.get("db_path")
        text_path = request.form.get("db_path")
        uploaded_file = request.files.get("db_file")
        new_db_path = resolve_db_path(text_path, uploaded_file)

        if new_db_path and os.path.exists(new_db_path):
            if old_db_path:
                old_db_name = os.path.basename(old_db_path)
                history = session.get("history", [])
                for item in history:
                    if item.get("db") == old_db_name:
                        item["expired"] = True
                session["history"] = history

                if "uploads" in old_db_path and os.path.exists(old_db_path):
                    try:
                        os.remove(old_db_path)
                    except:
                        pass

                message = "🔄 Database switched (previous DB removed for privacy)"
            else:
                message = "✅ Database loaded successfully"

            session["db_path"] = new_db_path
            session["conversation"] = []  # 🔥 RESET CONTEXT

        else:
            message = "❌ Invalid database path or file"

    # -------------------------
    # CONFIRM EXECUTION
    # -------------------------
    elif "confirm_sql" in request.form:
        sql = request.form.get("confirm_sql")
        db_path = session.get("db_path")
        history = session.get("history", [])

        is_blocked = any(item.get("cancelled") for item in history if item.get("sql") == sql)

        if not is_blocked:
            response = run_query(db_path, sql, confirm=True)

            entry = {
                "query": "⚠️ Confirmed Execution",
                "sql": sql,
                "type": response["type"],
                "data": response.get("data", []),
                "columns": response.get("columns", []),
                "message": response.get("message"),
                "explanation": response.get("explanation"),  # 🔥 NEW
                "db": os.path.basename(db_path),
                "expired": False
            }

            history = [item for item in history if not (item["type"] == "warning" and item["sql"] == sql)]
            history.insert(0, entry)
            session["history"] = history

    # -------------------------
    # CANCEL EXECUTION
    # -------------------------
    elif "cancel_sql" in request.form:
        sql = request.form.get("cancel_sql")
        history = session.get("history", [])
        for item in history:
            if item.get("sql") == sql:
                item["cancelled"] = True
        session["history"] = history
        message = "❌ Query cancelled permanently"

    # -------------------------
    # SUGGESTION CLICK
    # -------------------------
    elif "suggestion_value" in request.form:
        time.sleep(1)

        val = request.form.get("suggestion_value")
        orig = request.form.get("original_query")
        user_input = f"{orig} {val}"
        db_path = session.get("db_path")

        schema = get_schema(db_path)

        conversation = session.get("conversation", [])
        sql = nl_to_sql(user_input, schema, conversation_history=conversation)

        conversation.append({"user": user_input, "sql": sql})
        session["conversation"] = conversation[-5:]

        response = run_query(db_path, sql, user_input=user_input)

        entry = {
            "query": user_input,
            "sql": sql,
            "type": response["type"],
            "data": response.get("data", []),
            "columns": response.get("columns", []),
            "message": response.get("message"),
            "suggestions": response.get("suggestions", []),
            "explanation": response.get("explanation"),  # 🔥 NEW
            "db": os.path.basename(db_path),
            "expired": False
        }

        history = session["history"]
        history.insert(0, entry)
        session["history"] = history

    # -------------------------
    # RUN QUERY
    # -------------------------
    elif "run_query" in request.form:
        user_input = request.form.get("query")
        db_path = session.get("db_path")

        if not db_path:
            message = "❌ Please select a database first"

        elif not user_input:
            message = "❌ Please enter a query"

        else:
            time.sleep(1)

            schema = get_schema(db_path)

            conversation = session.get("conversation", [])
            sql = nl_to_sql(user_input, schema, conversation_history=conversation)

            conversation.append({"user": user_input, "sql": sql})
            session["conversation"] = conversation[-5:]

            response = run_query(db_path, sql, user_input=user_input)

            entry = {
                "query": user_input,
                "sql": sql,
                "type": response["type"],
                "message": response.get("message"),
                "data": response.get("data", []),
                "columns": response.get("columns", []),
                "suggestions": response.get("suggestions", []),
                "explanation": response.get("explanation"),  # 🔥 NEW
                "db": os.path.basename(db_path),
                "expired": False,
                "cancelled": False
            }

            history = session["history"]
            history.insert(0, entry)
            session["history"] = history

    # -------------------------
    # DELETE / CLEAR
    # -------------------------
    elif "delete_index" in request.form:
        idx = int(request.form.get("delete_index"))
        history = session.get("history", [])
        if 0 <= idx < len(history):
            history.pop(idx)
            session["history"] = history

    elif "clear_all" in request.form:
        session["history"] = []

    # -------------------------
    # REFRESH TABLES
    # -------------------------
    current_db = session.get("db_path")
    tables = get_all_tables(current_db) if current_db and os.path.exists(current_db) else []

    # -------------------------
    # RENDER
    # -------------------------
    if request.headers.get("HX-Request"):
        return render_template(
            "index.html",
            history=session.get("history", []),
            message=message,
            db_path=current_db,
            tables=tables,
            partial=True
        )

    return render_template(
        "index.html",
        history=session.get("history", []),
        message=message,
        db_path=current_db,
        tables=tables,
        partial=False
    )

if __name__ == "__main__":
    app.run(debug=True)