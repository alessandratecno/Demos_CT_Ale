from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Compatibilidade: alguns ambientes/plug-ins tentam importar MySQLdb.
# O PyMySQL fornece esse módulo via alias, evitando ModuleNotFoundError.
try:
    import MySQLdb  # type: ignore  # noqa: F401
except ModuleNotFoundError:
    import pymysql

    pymysql.install_as_MySQLdb()

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for
from mysql.connector import Error


def resource_path(relative_path: str) -> Path:
    """Retorna caminho para arquivos de template/static em execução normal ou empacotada."""
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / relative_path
    return Path(__file__).resolve().parent / relative_path


def writable_config_path() -> Path:
    """Sempre grava config ao lado do executável (ou do app.py no modo dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "db_config.json"
    return Path(__file__).resolve().parent / "db_config.json"


app = Flask(
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(resource_path("static")),
)
app.secret_key = "notasegura-local-secret"

CONFIG_PATH = writable_config_path()
DEFAULT_CONFIG = {
    "host": "notasegura-cluster.cluster-cyswk2h7td5h.us-east-1.rds.amazonaws.com",
    "port": 53861,
    "database": "notasegura",
    "user": "",
    "password": "",
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()

    merged = DEFAULT_CONFIG.copy()
    merged.update(saved)
    return merged


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_connection(config: dict[str, Any]):
    return mysql.connector.connect(
        host=config["host"],
        port=int(config["port"]),
        database=config["database"],
        user=config["user"],
        password=config["password"],
        connection_timeout=8,
    )


@app.route("/", methods=["GET", "POST"])
def login():
    config = load_config()

    if request.method == "POST":
        action = request.form.get("action")
        submitted = {
            "host": request.form.get("host", "").strip(),
            "port": int(request.form.get("port", "0") or 0),
            "database": request.form.get("database", "").strip(),
            "user": request.form.get("user", "").strip(),
            "password": request.form.get("password", ""),
        }

        if action == "save":
            save_config(submitted)
            flash("Configuração salva com sucesso.", "success")
            return redirect(url_for("login"))

        if action == "test":
            try:
                conn = get_connection(submitted)
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                conn.close()
                flash("Conexão realizada com sucesso.", "success")
            except Error as exc:
                flash(f"Falha na conexão: {exc}", "error")
            config = submitted

    return render_template("login.html", config=config)


@app.route("/delecao", methods=["GET", "POST"])
def delecao():
    config = load_config()
    table_options: list[str] = []
    selected_table = ""
    cnpj = ""
    user_id = ""
    sql_output = ""

    if request.method == "POST":
        cnpj = request.form.get("cnpj", "").strip()
        selected_table = request.form.get("table", "")

        if not cnpj:
            flash("Informe um CNPJ para buscar o usuário.", "error")
            return render_template(
                "delecao.html",
                table_options=table_options,
                selected_table=selected_table,
                cnpj=cnpj,
                user_id=user_id,
                sql_output=sql_output,
            )

        try:
            conn = get_connection(config)
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE users.cnpj = %s", (cnpj,))
                user = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT TABLE_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE REFERENCED_TABLE_NAME = 'users'
                    AND REFERENCED_COLUMN_NAME = 'id'
                    AND TABLE_SCHEMA = %s
                    ORDER BY TABLE_NAME
                    """,
                    (config["database"],),
                )
                table_options = [row["TABLE_NAME"] for row in cursor.fetchall()]

            if not user:
                flash("Nenhum usuário encontrado para este CNPJ.", "error")
            else:
                user_id = str(user["id"])
                target_tables = table_options
                if selected_table and selected_table != "__all__":
                    target_tables = [selected_table]

                if not target_tables:
                    flash("Nenhuma tabela relacionada ao users.id foi encontrada.", "error")
                else:
                    sql_lines = [f"DELETE FROM {table} WHERE user_id = {user_id};" for table in target_tables]
                    sql_output = "\n".join(sql_lines)
                    flash("SQL gerado com sucesso.", "success")

            conn.close()
        except Error as exc:
            flash(f"Erro ao consultar banco: {exc}", "error")

    return render_template(
        "delecao.html",
        table_options=table_options,
        selected_table=selected_table,
        cnpj=cnpj,
        user_id=user_id,
        sql_output=sql_output,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
