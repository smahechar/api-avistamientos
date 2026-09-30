"""API REST de registro de avistamientos de aves (Flask + SQLite)."""
import os
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, request

CAMPOS = ("especie", "lugar", "fecha", "observador")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS avistamientos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    especie     TEXT NOT NULL,
    lugar       TEXT NOT NULL,
    fecha       TEXT NOT NULL,
    observador  TEXT NOT NULL
);
"""


def create_app(db_path=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False  # que "colibrí" no salga como \u00ed
    app.json.sort_keys = False
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "avistamientos.db")

    # ---------- Base de datos ----------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with sqlite3.connect(app.config["DB_PATH"]) as conn:
        conn.executescript(ESQUEMA)
    conn.close()

    # ---------- Utilidades ----------
    def error(mensaje, codigo):
        return jsonify({"error": mensaje}), codigo

    def validar(datos):
        """Devuelve (datos_limpios, mensaje_error)."""
        if not isinstance(datos, dict):
            return None, "El cuerpo debe ser un objeto JSON."
        faltantes = [
            c for c in CAMPOS
            if not isinstance(datos.get(c), str) or not datos[c].strip()
        ]
        if faltantes:
            return None, f"Faltan datos o son inválidos: {', '.join(faltantes)}."
        limpios = {c: datos[c].strip() for c in CAMPOS}
        try:
            datetime.strptime(limpios["fecha"], "%Y-%m-%d")
        except ValueError:
            return None, "La fecha debe tener formato AAAA-MM-DD y ser válida."
        return limpios, None

    def buscar(id_):
        fila = get_db().execute(
            "SELECT * FROM avistamientos WHERE id = ?", (id_,)
        ).fetchone()
        return dict(fila) if fila else None

    # ---------- Endpoints ----------
    @app.get("/avistamientos")
    def listar():
        filas = get_db().execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
        return jsonify([dict(f) for f in filas]), 200

    # Bonus. Se declara con <int:id> en las demás rutas, así no hay conflicto.
    @app.get("/avistamientos/resumen")
    def resumen():
        filas = get_db().execute(
            "SELECT especie, COUNT(*) AS total FROM avistamientos "
            "GROUP BY especie ORDER BY total DESC, especie"
        ).fetchall()
        return jsonify({f["especie"]: f["total"] for f in filas}), 200

    @app.get("/avistamientos/<int:id_>")
    def ver(id_):
        av = buscar(id_)
        if av is None:
            return error("Avistamiento no encontrado.", 404)
        return jsonify(av), 200

    @app.post("/avistamientos")
    def crear():
        datos, msg = validar(request.get_json(silent=True))
        if msg:
            return error(msg, 400)
        db = get_db()
        cur = db.execute(
            "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
            "VALUES (:especie, :lugar, :fecha, :observador)",
            datos,
        )
        db.commit()
        return jsonify(buscar(cur.lastrowid)), 201

    @app.put("/avistamientos/<int:id_>")
    def actualizar(id_):
        if buscar(id_) is None:
            return error("Avistamiento no encontrado.", 404)
        datos, msg = validar(request.get_json(silent=True))
        if msg:
            return error(msg, 400)
        db = get_db()
        db.execute(
            "UPDATE avistamientos SET especie = :especie, lugar = :lugar, "
            "fecha = :fecha, observador = :observador WHERE id = :id",
            {**datos, "id": id_},
        )
        db.commit()
        return jsonify(buscar(id_)), 200

    @app.delete("/avistamientos/<int:id_>")
    def eliminar(id_):
        db = get_db()
        cur = db.execute("DELETE FROM avistamientos WHERE id = ?", (id_,))
        db.commit()
        if cur.rowcount == 0:
            return error("Avistamiento no encontrado.", 404)
        return "", 204

    # ---------- Errores en JSON ----------
    @app.errorhandler(404)
    def no_encontrado(_e):
        return error("Recurso no encontrado.", 404)

    @app.errorhandler(405)
    def metodo_no_permitido(_e):
        return error("Método no permitido.", 405)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
