import requests


NUMERO_WHATSAPP = "524151407013"

APIKEY_CALLMEBOT = "8372026"


class WhatsApp:

    def enviar(
        self,
        nombre,
        grado,
        grupo,
        emocion
    ):

        mensaje = f"""
📢 Nueva respuesta personal FeelTech

👤 Nombre: {nombre}
🎓 Grado: {grado}
🏫 Grupo: {grupo}
😊 Emoción: {emocion}
"""


        try:

            respuesta = requests.get(
                "https://api.callmebot.com/whatsapp.php",

                params={

                    "phone":
                    NUMERO_WHATSAPP,

                    "text":
                    mensaje,

                    "apikey":
                    APIKEY_CALLMEBOT
                }
            )


            print(
                "Respuesta de CallMeBot:",
                respuesta.text
            )


        except Exception as e:

            print(
                "Error al enviar WhatsApp:",
                e
            )
