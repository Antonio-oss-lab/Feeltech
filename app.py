from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

grado_guardado = ""
grupo_guardado = ""

def crear_db():
    conexion = sqlite3.connect("data_base_1.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grado TEXT,
            grupo TEXT,
            emocion TEXT
        )
        """
    )

    conexion.commit()
    conexion.close()

crear_db()

@app.route("/")
def inicio():
    return render_template("result_student.html")

@app.route("/volver")
def volver():
    return redirect(url_for("inicio"))

@app.route("/seleccion", methods=["POST"])
def seleccion():
    boton = request.form["boton"]

    if boton == "admin":
        return render_template("key.html")

    elif boton == "student":
        return render_template("select_1.html")

@app.route("/grado/<grado>")
def grado(grado):
    global grado_guardado
    grado_guardado = grado
    return render_template("select_a.html")

@app.route("/grupo/<grupo>")
def grupo(grupo):
    global grupo_guardado
    grupo_guardado = grupo
    return render_template("select_e.html")

@app.route("/emocion/<emocion>")
def emocion(emocion):
    conexion = sqlite3.connect("data_base_1.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO alumnos (grado, grupo, emocion)
        VALUES (?, ?, ?)
        """,
        (grado_guardado, grupo_guardado, emocion)
    )

    conexion.commit()
    conexion.close()

    return render_template("volver.html")

@app.route("/key")
def key():
    return render_template("key.html")

@app.route("/datos", methods=["GET", "POST"])
def datos():
    if request.method == "GET":
        return render_template("key.html")

    password = request.form.get("password")

    if password == "1234":
        emociones = [
            "Hoy tuve un buen día",
            "Me siento tranquilo",
            "Todo normal por ahora",
            "Estoy muy cansado",
            "Siento mucha presión",
            "Estoy preocupado por muchas cosas",
            "No tengo ganas de convivir",
            "Siento que nadie me entiende",
            "Me siento muy enojado",
            "Hoy me siento muy mal",
            "Me siento muy nervioso",
            "Me siento apartado del grupo"
        ]

        grupos = [
            "1A", "1B", "1C",
            "2A", "2B", "2C",
            "3A", "3B", "3C"
        ]

        conexion = sqlite3.connect("data_base_1.db")
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT grado, grupo, emocion, COUNT(*)
            FROM alumnos
            GROUP BY grado, grupo, emocion
        """)

        registros = cursor.fetchall()
        conexion.close()

        resumen = {}

        for grupo in grupos:
            resumen[grupo] = {}
            for emocion in emociones:
                resumen[grupo][emocion] = 0

        for grado, grupo, emocion, cantidad in registros:
            if grado is None or grupo is None or emocion is None:
                continue

            clave_grupo = str(grado) + str(grupo)

            if clave_grupo in resumen and emocion in resumen[clave_grupo]:
                resumen[clave_grupo][emocion] = cantidad

        totales_emocion = {}

        for emocion in emociones:
            total = 0
            for grupo in grupos:
                total += resumen[grupo][emocion]

            totales_emocion[emocion] = total

        total_general = sum(totales_emocion.values())

        return render_template(
            "final.html",
            emociones=emociones,
            grupos=grupos,
            resumen=resumen,
            totales_emocion=totales_emocion,
            total_general=total_general
        )

    else:
        return render_template(
            "key.html",
            error="Contraseña incorrecta"
        )

if __name__ == "__main__":
    app.run(debug=True)