"""
@File    :   exceptions.py
@Time    :   2023/04/23 09:38:38
@Author  :   Patricia Hernando Fernández
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""
from flask_babel import gettext


messages = {
    "krini_exception_default": gettext(
        "Ha ocurrido un error inesperado. Por favor, inténtelo de nuevo más tarde."
    ),
    "krini_not_logged_exception_default": gettext(
        "Debe iniciar sesión para acceder a esta página."
    ),
    "krini_db_exception_default": gettext(
        "Ha ocurrido un error en la base de datos. Inténtelo de nuevo más adelante."
    ),
    "not_callable_url": gettext(
        "No se ha podido llamar ni reconstruir la URL %s."
    )
    + gettext("Tampoco existe información en la base de datos acerca de ella."),
    "no_models_available": gettext(
        "No hay ningún modelo disponible. Inténtalo de nuevo más tarde."
    ),
    "no_info_display_dashboard": gettext(
        "Realiza un análisis para acceder al dashboard y visualizar resultados."
    ),
    "no_info_available": gettext(
        "La información para mostrar ha caducado o no está disponible."
    ),
}


def get_message(identifier, params=[]):
    """Returns a message translated and formatted if needed.

    Args:
        identifier (str): identifier of the message
        params (list, optional): parameters to format the message. Defaults to [].

    Returns:
        str: message formatted and translated
    """

    try:
        if len(params) == 0:
            return messages[identifier]

        else:
            return messages[identifier] % params[0]

    except (KeyError, IndexError):
        return gettext("No hay un mensaje disponible")
