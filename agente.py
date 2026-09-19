from data_base import Database


db = Database()


# ==========================================
# INTENCIONES
# ==========================================

INTENCIONES = {

    "estado_grupo": [
        "como esta",
        "como se encuentra",
        "estado de",
        "situacion de",
        "como va"
    ],

    "curso_peor": [
        "que curso esta peor",
        "cual curso esta peor",
        "grupo peor",
        "curso mas mal",
        "grupo mas mal"
    ],

    "comparar_grupos": [
        "compara",
        "comparar",
        "diferencia entre",
        "que grupo esta peor entre"
    ],

    "emocion_grupo": [
        "cuantos estan",
        "cuantos alumnos estan",
        "cuantas personas estan"
    ]
}


# ==========================================
# DETECTAR INTENCIÓN
# ==========================================

def detectar_intencion(pregunta):

    pregunta = pregunta.lower()

    for intencion, frases in INTENCIONES.items():

        for frase in frases:

            if frase in pregunta:

                return intencion

    return None


# ==========================================
# EXTRAER GRUPOS
# ==========================================

def extraer_grupos(pregunta):

    pregunta = pregunta.upper()

    grupos_validos = [

        "1A",
        "1B",
        "1C",

        "2A",
        "2B",
        "2C",

        "3A",
        "3B",
        "3C"
    ]


    encontrados = []


    for grupo in grupos_validos:

        if grupo in pregunta:

            encontrados.append(
                grupo
            )


    return encontrados


# ==========================================
# BUSCAR EMOCIÓN
# ==========================================

def detectar_emocion(pregunta):

    pregunta = pregunta.lower()


    emociones = {

        "nervioso":
        "Me siento muy nervioso",

        "nerviosos":
        "Me siento muy nervioso",

        "cansado":
        "Estoy muy cansado",

        "cansados":
        "Estoy muy cansado",

        "enojado":
        "Me siento muy enojado",

        "enojados":
        "Me siento muy enojado",

        "presion":
        "Siento mucha presión",

        "presión":
        "Siento mucha presión",

        "preocupado":
        "Estoy preocupado por muchas cosas",

        "preocupados":
        "Estoy preocupado por muchas cosas"
    }


    for palabra, emocion in emociones.items():

        if palabra in pregunta:

            return emocion


    return None

def procesar_pregunta(pregunta):

    pregunta = pregunta.strip()


    if pregunta == "":

        return "Escribe una pregunta."


    intencion = detectar_intencion(
        pregunta
    )


    grupos = extraer_grupos(
        pregunta
    )

    if intencion == "estado_grupo":

        if len(grupos) != 1:

            return (
                "Necesito que indiques "
                "un grupo, por ejemplo: "
                "¿Cómo está 2B?"
            )


        grupo = grupos[0]


        estado = db.obtener_estado_grupo(
            grupo
        )


        if estado["total"] == 0:

            return (
                "No hay respuestas "
                "registradas para "
                + grupo
                + "."
            )


        return (

            "El grupo "
            + grupo
            + " tiene "
            + str(estado["total"])
            + " respuestas. "

            "Hay "
            + str(estado["positivo"])
            + " respuestas positivas y "

            + str(estado["negativo"])
            + " respuestas asociadas "
            "a emociones negativas. "

            "El porcentaje de respuestas "
            "negativas es "
            + str(
                round(
                    estado["porcentaje_negativo"],
                    1
                )
            )
            + "%."
        )

    if intencion == "curso_peor":

        peor = db.obtener_curso_peor()

        if peor is None:

            return (
                "Todavía no hay "
                "suficientes datos."
            )

        return (

            "Según los datos registrados, "
            "el grupo con mayor porcentaje "
            "de respuestas negativas es "

            + peor["grupo"]

            + ", con "

            + str(
                round(
                    peor["porcentaje_negativo"],
                    1
                )
            )

            + "%."
        )

    if intencion == "comparar_grupos":

        if len(grupos) != 2:

            return (
                "Necesito dos grupos "
                "para comparar. "
                "Por ejemplo: "
                "Compara 1A con 3B."
            )


        grupo1 = db.obtener_estado_grupo(
            grupos[0]
        )

        grupo2 = db.obtener_estado_grupo(
            grupos[1]
        )


        if (
            grupo1["total"] == 0
            or
            grupo2["total"] == 0
        ):

            return (
                "Uno de los grupos no tiene "
                "respuestas suficientes "
                "para realizar la comparación."
            )

        return (

            grupo1["grupo"]

            + " tiene "

            + str(
                round(
                    grupo1["porcentaje_negativo"],
                    1
                )
            )

            + "% de respuestas negativas, "
            "mientras que "

            + grupo2["grupo"]

            + " tiene "

            + str(
                round(
                    grupo2["porcentaje_negativo"],
                    1
                )
            )

            + "%."
        )

    if intencion == "emocion_grupo":

        if len(grupos) != 1:

            return (
                "Necesito que indiques "
                "un grupo."
            )


        emocion = detectar_emocion(
            pregunta
        )


        if emocion is None:

            return (
                "No pude identificar "
                "la emoción. "
                "Por ejemplo puedes "
                "preguntar: "
                "¿Cuántos alumnos están "
                "nerviosos en 2C?"
            )


        grupo = grupos[0]


        cantidad = db.obtener_emocion_grupo(
            grupo,
            emocion
        )


        return (

            "En "
            + grupo
            + " hay "
            + str(cantidad)
            + " respuestas relacionadas "
            "con esa emoción."
        )

    return (

        "No entendí la pregunta. "

        "Puedes preguntar, por ejemplo: "

        "¿Cómo está 2B?, "

        "¿Qué curso está peor?, "

        "Compara 1A con 3B, "

        "o "

        "¿Cuántos alumnos están "
        "nerviosos en 2C?"
    )