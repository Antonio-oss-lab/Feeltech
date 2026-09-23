from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import requests

from datos import datos_feeltech
from data_base import Database
from agente import procesar_pregunta


app = Flask(__name__)

app.secret_key = "feeltech_clave_secreta"


# ==========================================
# WHATSAPP
# ==========================================

NUMERO_WHATSAPP = "5214151407013"

APIKEY_CALLMEBOT = "8372026"


def enviar_whatsapp(
    nombre,
    grado,
    grupo,
    emocion
):

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

        print(
            "Respuesta de CallMeBot:",
            respuesta.text
        )

        print(
            "Código:",
            respuesta.status_code
        )

    except Exception as e:

        print(
            "Error al enviar WhatsApp:",
            e
        )


# ==========================================
# BASE DE DATOS
# ==========================================

db = Database()


# ==========================================
# INICIO
# ==========================================

@app.route("/")
def inicio():

    return render_template(
        "result_student.html"
    )


# ==========================================
# VOLVER
# ==========================================

@app.route("/volver")
def volver():

    return render_template(
        "volver.html"
    )


# ==========================================
# REINICIAR
# ==========================================

@app.route("/reiniciar")
def reiniciar():

    session.clear()

    return redirect(
        url_for("inicio")
    )


# ==========================================
# SELECCIÓN ADMIN / ESTUDIANTE
# ==========================================

@app.route(
    "/seleccion",
    methods=["POST"]
)
def seleccion():

    boton = request.form.get(
        "boton"
    )

    if boton == "admin":

        return render_template(
            "key.html"
        )

    elif boton == "student":

        return render_template(
            "select_1.html"
        )

    return redirect(
        url_for("inicio")
    )


# ==========================================
# SELECCIONAR GRADO
# ==========================================

@app.route("/grado/<grado>")
def grado(grado):

    session["grado"] = grado

    return render_template(
        "select_a.html"
    )


# ==========================================
# SELECCIONAR GRUPO
# ==========================================

@app.route("/grupo/<grupo>")
def grupo(grupo):

    session["grupo"] = grupo

    return render_template(
        "select_e.html"
    )


# ==========================================
# SELECCIONAR EMOCIÓN
# ==========================================

@app.route("/emocion/<emocion>")
def emocion(emocion):

    session["emocion"] = emocion

    return render_template(
        "anonimo.html"
    )


# ==========================================
# ANÓNIMO O PERSONAL
# ==========================================

@app.route("/anonimo/<respuesta>")
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


# ==========================================
# GUARDAR RESPUESTA PERSONAL
# ==========================================

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

    # Guardar en la base de datos

    db.guardar_respuesta_personal(

        grado_guardado,
        grupo_guardado,
        nombre,
        emocion_guardada
    )

    # Enviar a WhatsApp

    enviar_whatsapp(

        nombre,
        grado_guardado,
        grupo_guardado,
        emocion_guardada
    )

    # Limpiar sesión

    session.clear()

    return redirect(
        url_for("volver")
    )


# ==========================================
# CONTRASEÑA ADMIN
# ==========================================

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


# ==========================================
# RESPUESTAS GENERALES
# ==========================================

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
            str(grado)
            +
            str(grupo)
        )

        if (
            clave_grupo in resumen
            and
            emocion in resumen[
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


# ==========================================
# RESPUESTAS PERSONALES
# ==========================================

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


# ==========================================
# AGENTE FEELTECH
# ==========================================

@app.route(
    "/agente",
    methods=["GET", "POST"]
)
def agente():

    respuesta = ""

    if request.method == "POST":

        pregunta = request.form.get(
            "pregunta"
        )

        respuesta = procesar_pregunta(
            pregunta
        )

    return render_template(

        "agente.html",

        respuesta=respuesta
    )


# ==========================================
# EJECUTAR
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
