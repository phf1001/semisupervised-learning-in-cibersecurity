"""
@File    :   exceptions.py
@Time    :   2023/04/23 09:38:38
@Author  :   Patricia Hernando Fernández
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""
from flask_babel import gettext


def get_exception_message(identifier) -> str:
    if identifier == "already_logged":
        return gettext(
            "Ya has iniciado sesión. Cierra sesión para crear una cuenta nueva."
        )

    return "Mensaje no encontrado"


def get_form_message(identifier):
    """Returns the message for the form with the given identifier.
    Also translates the message to the current language.

    Args:
        identifier (str): string identifier of the message

    Returns:
        str: message formatted and translated
    """
    if identifier == "no_username":
        return gettext("Por favor, introduce un nombre de usuario.")

    if identifier == "no_password":
        return gettext("Por favor, introduce una contraseña.")

    if identifier == "no_email":
        return gettext("Por favor, introduce un email.")

    if identifier == "incorrect_email":
        return gettext("Por favor, introduce un email válido.")

    if identifier == "used_username":
        return gettext("El nombre de usuario ya está en uso.")

    if identifier == "used_email":
        return gettext("El email ya está en uso.")

    if identifier == "no_name":
        return gettext("Por favor, introduce tu nombre propio.")

    if identifier == "no_surname":
        return gettext("Por favor, introduce tus apellidos.")

    if identifier == "no_credentials":
        return gettext("Por favor, introduce tus credenciales.")

    if identifier == "incorrect_credentials":
        return gettext("Las credenciales introducidas no son correctas.")

    if identifier == "account_created":
        return (
            gettext("Usuario creado con éxito.")
            + '<a href="/login">'
            + gettext(" Inicia sesión")
            + "</a>"
        )

    if identifier == "account_not_created":
        return gettext(
            "No se ha podido crear la cuenta. Inténtelo de nuevo más tarde."
        )

    return "Mensaje no encontrado"


def get_message(identifier, params=[]):
    """
    Returns the message for the given identifier.
    Also translates the message to the current language.

    Args:
        identifier (str): identifier of the message
        params (list, optional): parameters to format the message. Defaults to [].
    Returns:
        str: message formatted and translated
    """
    if identifier == "krini_exception_default":
        return gettext(
            "Ha ocurrido un error inesperado. Por favor, inténtelo de nuevo más tarde."
        )

    if identifier == "krini_not_logged_exception_default":
        return gettext("Debe iniciar sesión para acceder a esta página.")

    if identifier == "krini_db_exception_default":
        return gettext(
            "Ha ocurrido un error en la base de datos. Inténtelo de nuevo más adelante."
        )

    if identifier == "not_callable_url":
        return (
            gettext("No se ha podido llamar ni reconstruir la URL %s.")
            % params[0]
            + " "
            + gettext(
                "Tampoco existe información en la base de datos acerca de ella."
            )
        )

    if identifier == "no_models_available":
        return gettext(
            "No hay ningún modelo disponible. Inténtalo de nuevo más tarde."
        )

    if identifier == "no_info_display_dashboard":
        return gettext(
            "Realiza un análisis para acceder al dashboard y visualizar resultados."
        )

    if identifier == "no_info_available":
        return gettext(
            "La información para mostrar ha caducado o no está disponible."
        )

    if identifier == "language_changed":
        return gettext("Idioma cambiado correctamente.")

    if identifier == "language_not_changed":
        return gettext("No se ha podido cambiar el idioma.")
