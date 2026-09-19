import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data_base_1.db"
)


class Database:

    def __init__(self):

        self.db_path = DB_PATH


    def conectar(self):

        return sqlite3.connect(
            self.db_path
        )


    # ==========================================
    # GUARDAR RESPUESTA GENERAL
    # ==========================================

    def guardar_respuesta_general(
        self,
        grado,
        grupo,
        emocion
    ):

        conexion = self.conectar()

        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO alumnos
            (grado, grupo, emocion)
            VALUES (?, ?, ?)
            """,
            (
                grado,
                grupo,
                emocion
            )
        )

        conexion.commit()

        conexion.close()


    # ==========================================
    # GUARDAR RESPUESTA PERSONAL
    # ==========================================

    def guardar_respuesta_personal(
        self,
        grado,
        grupo,
        nombre,
        emocion
    ):

        conexion = self.conectar()

        cursor = conexion.cursor()

        fecha_hora = datetime.now()

        fecha = fecha_hora.strftime(
            "%d/%m/%Y"
        )

        hora = fecha_hora.strftime(
            "%H:%M:%S"
        )

        cursor.execute(
            """
            INSERT INTO respuestas_personales
            (grado, grupo, nombre, emocion, fecha, hora)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                grado,
                grupo,
                nombre,
                emocion,
                fecha,
                hora
            )
        )

        conexion.commit()

        conexion.close()


    # ==========================================
    # OBTENER RESPUESTAS GENERALES
    # ==========================================

    def obtener_resumen(self):

        conexion = self.conectar()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT grado, grupo, emocion, COUNT(*)
            FROM alumnos
            GROUP BY grado, grupo, emocion
            """
        )

        registros = cursor.fetchall()

        conexion.close()

        return registros


    # ==========================================
    # OBTENER RESPUESTAS PERSONALES
    # ==========================================

    def obtener_respuestas_personales(self):

        conexion = self.conectar()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id, grado, grupo, nombre,
                   emocion, fecha, hora
            FROM respuestas_personales
            ORDER BY id DESC
            """
        )

        respuestas = cursor.fetchall()

        conexion.close()

        return respuestas


    # ==========================================
    # OBTENER DATOS DE UN GRUPO
    # ==========================================

    def obtener_datos_grupo(self, grupo):

        conexion = self.conectar()

        cursor = conexion.cursor()

        grado = grupo[0]

        grupo_letra = grupo[1]

        cursor.execute(
            """
            SELECT emocion, COUNT(*)
            FROM alumnos
            WHERE grado = ?
            AND grupo = ?
            GROUP BY emocion
            ORDER BY COUNT(*) DESC
            """,
            (
                grado,
                grupo_letra
            )
        )

        resultados = cursor.fetchall()

        conexion.close()

        datos = {}

        total = 0

        for emocion, cantidad in resultados:

            datos[emocion] = cantidad

            total += cantidad

        return datos, total


    # ==========================================
    # OBTENER ESTADO DE UN GRUPO
    # ==========================================

    def obtener_estado_grupo(self, grupo):

        datos, total = self.obtener_datos_grupo(
            grupo
        )

        if total == 0:

            return {
                "grupo": grupo,
                "total": 0,
                "positivo": 0,
                "negativo": 0,
                "porcentaje_negativo": 0
            }


        emociones_positivas = [

            "Hoy tuve un buen día",

            "Me siento tranquilo",

            "Todo normal por ahora"
        ]


        emociones_negativas = [

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


        positivo = 0

        negativo = 0


        for emocion in emociones_positivas:

            positivo += datos.get(
                emocion,
                0
            )


        for emocion in emociones_negativas:

            negativo += datos.get(
                emocion,
                0
            )


        porcentaje_negativo = (
            negativo / total
        ) * 100


        return {

            "grupo": grupo,

            "total": total,

            "positivo": positivo,

            "negativo": negativo,

            "porcentaje_negativo": porcentaje_negativo,

            "emociones": datos
        }


    # ==========================================
    # OBTENER CURSO CON MAYOR PORCENTAJE NEGATIVO
    # ==========================================

    def obtener_curso_peor(self):

        grupos = [

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


        resultados = []


        for grupo in grupos:

            estado = self.obtener_estado_grupo(
                grupo
            )

            if estado["total"] > 0:

                resultados.append(
                    estado
                )


        if len(resultados) == 0:

            return None


        resultados.sort(
            key=lambda x:
            x["porcentaje_negativo"],
            reverse=True
        )


        return resultados[0]


    # ==========================================
    # CONTAR UNA EMOCIÓN EN UN GRUPO
    # ==========================================

    def obtener_emocion_grupo(
        self,
        grupo,
        emocion
    ):

        conexion = self.conectar()

        cursor = conexion.cursor()


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM alumnos
            WHERE grado = ?
            AND grupo = ?
            AND emocion = ?
            """,
            (
                grupo[0],
                grupo[1],
                emocion
            )
        )


        resultado = cursor.fetchone()

        conexion.close()


        return resultado[0]
