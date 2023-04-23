# Declares
NAIVE_BAYES_NAME = "Naive Bayes"
DECISION_TREE_NAME = "Árbol de decisión"
KNN_NAME = "k-vecinos más cercanos"

NAIVE_BAYES_KEY = "NB"
DECISION_TREE_KEY = "tree"
KNN_KEY = "kNN"

from flask_babel import gettext

import logging


def get_logger(
    name,
    file_name="log_krini",
    logger_level=logging.DEBUG,
    file_level=logging.DEBUG,
):
    """
    Returns a logger with the given name and the given
    parameters.

    Args:
        name (str): logger name.
        file_name(str, optional): file name. Defaults to "log_krini".
        logger_level (str, optional): Defaults to logging.DEBUG.
        file_level (str, optional): Defaults to logging.DEBUG.

    Returns:
        object: logger object.
    """
    new_logger = logging.getLogger(name)

    if new_logger.hasHandlers():
        new_logger.handlers.clear()

    new_logger.setLevel(logger_level)

    fh = logging.FileHandler(file_name)
    fh.setLevel(file_level)
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    new_logger.addHandler(fh)

    return new_logger


logger = get_logger("krini-frontend")

# Messages
SALUDATION = gettext("Hola")
KRINI_EXCEPTION_DEFAULT = gettext("Ha ocurrido una excepción en la aplicación.")
KRINI_EXCEPTION_DB_DEFAULT = "Ha ocurrido una excepción en la base de datos."
KRINI_EXCEPTION_NOT_LOGGED_DEFAULT = "No se ha iniciado sesión en Krini."

MSG_URL_NOT_CALLABLE_PT_1 = "No se ha podido llamar la url {} ni reconstruir. Tampoco se ha encontrado información en la base de datos acerca de esta URL."


MSG_URL_NOT_REACHEABLE = gettext(
    "La URL {} no puede ser llamada ni tampoco reconstruída. Comprueba la sintáxis {} y si la página está disponible e inténtalo de nuevo."
)
NO_MODEL_AVAILABLE = (
    "No hay ningún modelo disponible. Inténtalo de nuevo más tarde."
)
NO_INFO_DISPLAY_DASHBOARD = "No existe información para mostrar. Realiza un análisis para acceder al dashboard."
NO_INFO_DASHBOARD = "La información para mostrar ha caducado o no está disponible. Realiza otro análisis para acceder al dashboard."

FORMAT_SIMPLE = gettext("Oye meto aqui algo en medio a ver que se cuece")


class Messages:
    def get_not_callable_url(url):
        logger.info(
            "asdasd {}".format(
                gettext("No se ha podido llamar la url").__class__
            )
        )
        return (
            gettext("No se ha podido llamar la url")
            + url
            + gettext(
                "ni reconstruir. Tampoco se ha encontrado información en la base de datos acerca de esta URL."
            )
        )
