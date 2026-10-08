from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
    jsonify
)

import requests
import sqlite3
import os
import pyttsx3

from io import BytesIO

from datos import datos_feeltech
from data_base import Database


app = Flask(__name__)
app.secret_key = "feeltech_clave_secreta"

NUMERO_WHATSAPP = "5214151407013"

APIKEY_CALLMEBOT = "8372026"


PREGUNTAS_AUDIO = [
    "¿Cómo te sentiste hoy?",
    "¿Cómo te has sentido durante estos días?",
    "¿Hay algo que te haya hecho sentir bien?",
    "¿Hay algo que te haya preocupado o puesto nervioso?",
    "¿Qué crees que podría ayudarte a sentirte mejor?"
]


def enviar_whatsapp(nombre, grado, grupo, emocion):

    mensaje = f"""
Nueva respuesta personal FeelTech

Nombre: {nombre}
Grado: {grado}
Grupo: {grupo}
Emoción: {emocion}
"""

    try:

        respuesta = requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params={
                "phone": NUMERO_WHATSAPP,
                "text": mensaje,
                "apikey": APIKEY_CALLMEBOT
            },
            timeout=10
        )

        print("Respuesta de CallMeBot:", respuesta.text)
        print("Código:", respuesta.status_code)

    except Exception as e:

        print("Error al enviar WhatsApp:", e)


db = Database()


def crear_base_audio():

    conexion = sqlite3.connect("audios.db")

    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grado TEXT,
            grupo TEXT,
            nombre TEXT,
            numero_pregunta INTEGER,
            pregunta TEXT,
            respuesta_texto TEXT,
            audio_pregunta BLOB,
            audio_respuesta BLOB,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()

    conexion.close()


crear_base_audio()


def crear_audio_pregunta(texto):

    archivo = "pregunta_temporal.wav"

    try:

        motor = pyttsx3.init()

        motor.setProperty(
            "rate",
            125
        )

        motor.setProperty(
            "volume",
            1.0
        )

        voces = motor.getProperty(
            "voices"
        )

        if len(voces) > 0:

            motor.setProperty(
                "voice",
                voces[0].id
            )

        motor.save_to_file(
            texto,
            archivo
        )

        motor.runAndWait()

        motor.stop()

        if not os.path.exists(archivo):

            return None

        with open(
            archivo,
            "rb"
        ) as archivo_audio:

            audio = archivo_audio.read()

        os.remove(archivo)

        return audio

    except Exception as e:

        print(
            "Error creando audio de pregunta:",
            e
        )

        if os.path.exists(archivo):

            os.remove(archivo)

        return None


@app.route("/")
def inicio():

    return render_template(
        "result_student.html"
    )


@app.route("/audio")
def modo_audio():

    session.clear()

    return render_template(
        "audio.html",
        preguntas=PREGUNTAS_AUDIO
    )


@app.route(
    "/guardar_datos_audio",
    methods=["POST"]
)
def guardar_datos_audio():

    datos = request.get_json()

    if not datos:

        return jsonify({
            "ok": False,
            "mensaje": "No se recibieron datos"
        }), 400


    grado = datos.get("grado")

    grupo = datos.get("grupo")

    nombre = datos.get("nombre")


    if not grado or not grupo or not nombre:

        return jsonify({
            "ok": False,
            "mensaje": "Faltan datos"
        }), 400


    session["grado_audio"] = grado

    session["grupo_audio"] = grupo

    session["nombre_audio"] = nombre


    return jsonify({
        "ok": True
    })


@app.route(
    "/guardar_audio",
    methods=["POST"]
)
def guardar_audio():

    archivo = request.files.get("audio")

    if not archivo:

        return jsonify({
            "ok": False,
            "mensaje": "No se recibió el audio"
        }), 400


    numero_pregunta = request.form.get(
        "numero_pregunta"
    )

    pregunta = request.form.get(
        "pregunta"
    )

    respuesta_texto = request.form.get(
        "respuesta_texto"
    )


    audio_respuesta = archivo.read()


    audio_pregunta = crear_audio_pregunta(
        pregunta
    )


    conexion = sqlite3.connect(
        "audios.db"
    )

    cursor = conexion.cursor()


    cursor.execute("""
        INSERT INTO audios (
            grado,
            grupo,
            nombre,
            numero_pregunta,
            pregunta,
            respuesta_texto,
            audio_pregunta,
            audio_respuesta
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session.get("grado_audio"),
        session.get("grupo_audio"),
        session.get("nombre_audio"),
        numero_pregunta,
        pregunta,
        respuesta_texto,
        audio_pregunta,
        audio_respuesta
    ))


    conexion.commit()

    conexion.close()


    return jsonify({
        "ok": True
    })


@app.route("/audios")
def ver_audios():

    conexion = sqlite3.connect(
        "audios.db"
    )

    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()


    cursor.execute("""
        SELECT *
        FROM audios
        ORDER BY id DESC
    """)


    audios = cursor.fetchall()

    conexion.close()


    return render_template(
        "audios.html",
        audios=audios
    )


@app.route(
    "/escuchar_pregunta/<int:id>"
)
def escuchar_pregunta(id):

    conexion = sqlite3.connect(
        "audios.db"
    )

    cursor = conexion.cursor()


    cursor.execute(
        """
        SELECT audio_pregunta
        FROM audios
        WHERE id = ?
        """,
        (id,)
    )


    resultado = cursor.fetchone()

    conexion.close()


    if not resultado:

        return "Audio no encontrado", 404


    if resultado[0] is None:

        return "Audio de pregunta no encontrado", 404


    return send_file(
        BytesIO(resultado[0]),
        mimetype="audio/wav"
    )


@app.route(
    "/escuchar_audio/<int:id>"
)
def escuchar_audio(id):

    conexion = sqlite3.connect(
        "audios.db"
    )

    cursor = conexion.cursor()


    cursor.execute(
        """
        SELECT audio_respuesta
        FROM audios
        WHERE id = ?
        """,
        (id,)
    )


    resultado = cursor.fetchone()

    conexion.close()


    if not resultado:

        return "Audio no encontrado", 404


    if resultado[0] is None:

        return "Audio de respuesta no encontrado", 404


    return send_file(
        BytesIO(resultado[0]),
        mimetype="audio/webm"
    )


@app.route("/finalizar_audio")
def finalizar_audio():

    session.clear()

    return jsonify({
        "ok": True
    })


@app.route("/volver")
def volver():

    return render_template(
        "volver.html"
    )


@app.route("/reiniciar")
def reiniciar():

    session.clear()

    return redirect(
        url_for("inicio")
    )


@app.route("/seleccion/<tipo>")
def seleccion(tipo):

    if tipo == "admin":

        return render_template(
            "key.html"
        )

    elif tipo == "student":

        return render_template(
            "select_1.html"
        )

    return redirect(
        url_for("inicio")
    )


@app.route("/grado/<grado>")
def grado(grado):

    session["grado"] = grado

    return render_template(
        "select_a.html"
    )


@app.route("/grupo/<grupo>")
def grupo(grupo):

    session["grupo"] = grupo

    return render_template(
        "select_e.html"
    )


@app.route("/emocion/<emocion>")
def emocion(emocion):

    session["emocion"] = emocion

    return render_template(
        "anonimo.html"
    )


@app.route(
    "/anonimo/<respuesta>"
)
def anonimo(respuesta):

    if respuesta == "Personal":

        return render_template(
            "nombre.html"
        )


    grado_guardado = session.get(
        "grado"
    )

    grupo_guardado = session.get(
        "grupo"
    )

    emocion_guardada = session.get(
        "emocion"
    )


    db.guardar_respuesta_general(
        grado_guardado,
        grupo_guardado,
        emocion_guardada
    )


    session.clear()


    return redirect(
        url_for("volver")
    )


@app.route(
    "/guardar_nombre",
    methods=["POST"]
)
def guardar_nombre():

    nombre = request.form.get(
        "nombre"
    )


    grado_guardado = session.get(
        "grado"
    )

    grupo_guardado = session.get(
        "grupo"
    )

    emocion_guardada = session.get(
        "emocion"
    )


    db.guardar_respuesta_personal(
        grado_guardado,
        grupo_guardado,
        nombre,
        emocion_guardada
    )


    enviar_whatsapp(
        nombre,
        grado_guardado,
        grupo_guardado,
        emocion_guardada
    )


    session.clear()


    return redirect(
        url_for("volver")
    )


@app.route(
    "/datos",
    methods=["GET", "POST"]
)
def datos():

    if request.method == "GET":

        return render_template(
            "key.html"
        )


    password = request.form.get(
        "password"
    )


    if password == "1234":

        return render_template(
            "opciones_admin.html"
        )


    return render_template(
        "key.html",
        error="Contraseña incorrecta"
    )


@app.route("/respuestas_generales")
def respuestas_generales():

    registros = db.obtener_resumen()

    emociones = datos_feeltech[
        "emociones"
    ]

    grupos = datos_feeltech[
        "grupos_completos"
    ]


    resumen = {}


    for grupo in grupos:

        resumen[grupo] = {}


        for emocion in emociones:

            resumen[grupo][emocion] = 0


    for (
        grado,
        grupo,
        emocion,
        cantidad
    ) in registros:

        if (
            grado is None
            or grupo is None
            or emocion is None
        ):

            continue


        clave_grupo = (
            str(grado) +
            str(grupo)
        )


        if (
            clave_grupo in resumen
            and emocion in resumen[
                clave_grupo
            ]
        ):

            resumen[
                clave_grupo
            ][emocion] = cantidad


    totales_emocion = {}


    for emocion in emociones:

        total = 0


        for grupo in grupos:

            total += resumen[
                grupo
            ][emocion]


        totales_emocion[
            emocion
        ] = total


    total_general = sum(
        totales_emocion.values()
    )


    return render_template(
        "final.html",
        emociones=emociones,
        grupos=grupos,
        resumen=resumen,
        totales_emocion=totales_emocion,
        total_general=total_general
    )


@app.route(
    "/respuestas_personales"
)
def respuestas_personales():

    respuestas = (
        db.obtener_respuestas_personales()
    )


    return render_template(
        "respuestas_personales.html",
        respuestas=respuestas
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )