"""
@File    :   exceptions.py
@Time    :   2023/04/23 09:38:38
@Author  :   Patricia Hernando Fernández
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""
from flask_babel import gettext


def get_exception_message(identifier) -> str:
    """Returns the message for the exception with the given identifier.

    Args:
        identifier (str): identifier of the exception

    Returns:
        str: message formatted and translated
    """
    if identifier == "error_operation":
        return gettext("Error al realizar la operación solicitada.")

    if identifier == "already_logged":
        return gettext(
            "Ya has iniciado sesión. Cierra sesión para crear una cuenta nueva."
        )

    if identifier == "not_instance_found":
        return gettext("No se ha encontrado la instancia.")

    if identifier == "not_info_found":
        return gettext("No se ha encontrado la información.")

    if identifier == "log_to_report":
        return gettext(
            "Inicia sesión para reportar falsos positivos."
        ) + gettext("Gracias por tu colaboración.")

    if identifier == "report_url_error":
        return gettext(
            "¡Lo sentimos! No se ha podido registrar el falso resultado."
        ) + gettext(
            "Inténtalo de nuevo más adelante. Gracias por tu colaboración."
        )

    if identifier == "error_csv":
        return gettext("Se ha producido un error al subir los archivos .csv.")

    if identifier == "sets_generated_random":
        return gettext(
            "Se ha generado el conjunto de train y test aleatoriamente."
        )

    if identifier == "few_instances":
        return (
            gettext(
                "Error al crear el modelo. ¿Has comprobado que los ficheros de "
            )
            + gettext(
                "entrenamiento y test tengan un número mínimo de instancias?"
            )
            + gettext(" Parecen ser demasiado pocas.")
        )

    if identifier == "no_test_available":
        return (
            gettext("No hay instancias para testear el modelo")
            + gettext(" (han sido todas vistas durante el entrenamiento).")
            + gettext(
                " Prueba a subir un csv. Mostrando scores almacenados en la BD."
            )
        )

    if identifier == "error_load_model":
        return gettext("Error al cargar el modelo o alguno de sus parámetros.")

    if identifier == "vector_not_generated":
        return gettext("Operación no realizada: no se puede") + gettext(
            " generar el vector de características. La URL no está disponible."
        )

    if identifier == "error_load_vector":
        return gettext("Error extrayendo el vector de características.")

    if identifier == "error_TFIDF":
        return gettext("Error reconstruyendo el objeto TFIDF")

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

    if identifier == "IA_file_not_found":
        return gettext(
            "No se ha podido cargar el fichero de la IA. Lo sentimos."
        )

    if identifier == "error_storing_model_or_training_data":
        return gettext(
            "Error al guardar el modelo en la BD o los datos de entrenamiento."
        ) + gettext(" Comprueba que las instancias utilizadas están en la BD.")

    if identifier == "serialized_not_found":
        return gettext("No se ha encontrado el modelo serializado.")

    if identifier == "error_extracting_X_y":
        return gettext("Error al generar el dataset.")

    if identifier == "error_generating_dataset":
        return gettext("Error al generar el dataset de entrenamiento.")

    if identifier == "incorrect_file":
        return gettext("El fichero subido no existe o no es un csv.")

    if identifier == "incorrect_file_format":
        return gettext(
            "El fichero no tiene el formato correcto. Prueba a descargarlo desde "
        ) + gettext(
            "la aplicación (tiene que tener un id, 19 atributos y la etiqueta)."
        )

    if identifier == "error_updating_scores":
        return gettext(
            "No se han podido actualizar los scores en la base de datos."
        )

    if identifier == "base_cls_not_found":
        return gettext("Clasificador base no encontrado")

    if identifier == "protected_models":
        return (
            gettext(
                "¡Lo sentimos! Los modelos 1, 2 y 3 están protegidos. Aún así, la "
            )
            + gettext(
                "conexión con la base de datos es correcta y se muestra el mensaje de "
            )
            + gettext(
                "'eliminado correctamente' para que sepas que el método funciona."
            )
        )

    return get_message("Ha ocurrido una excepción. ¡Lo sentimos!")


def get_form_message(identifier) -> str:
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

    if identifier == "empty_url":
        return gettext("Por favor, introduce una URL.")

    if identifier == "url_too_long":
        return gettext(
            "Por favor, introduce una URL más corta (máximo 255 caracteres)."
        )

    if identifier == "description_too_long":
        return gettext(
            "Por favor, introduce una descripción más corta (máximo 511 caracteres)."
        )

    if identifier == "model_name_too_long":
        return gettext(
            "Por favor, introduce un nombre más corto (máximo 50 caracteres)."
        )

    if identifier == "username_too_long":
        return gettext(
            "Introduce un nombre de usuario más corto (máximo 63 caracteres)."
        )

    if identifier == "email_too_long":
        return gettext(
            "Por favor, introduce un email más corto (máximo 128 caracteres)."
        )

    if identifier == "first_name_too_long":
        return gettext(
            "Por favor, introduce un nombre propio más corto (máximo 63 caracteres)."
        )

    if identifier == "surname_too_long":
        return gettext(
            "Por favor, introduce unos apellidos más cortos (máximo 63 caracteres)."
        )

    if identifier == "no_option_selected":
        return gettext("Por favor, selecciona una opción en el desplegable.")

    if identifier == "invalid_version":
        return gettext("Introduce una versión válida.") + gettext(
            "Si no sabes qué poner, puedes probar a introducir un número entero."
        )

    if identifier == "empty_name":
        return gettext("Por favor, introduce un nombre.")

    if identifier == "empty_random_state":
        return gettext(
            "Por favor, introduce una semilla aleatoria o -1 en su defecto."
        )

    if identifier == "empty_train_percentage_instances":
        return gettext(
            "Por favor, introduce un porcentaje de instancias de entrenamiento."
        )

    if identifier == "invalid_train_percentage_instances":
        return gettext(
            "Por favor, introduce un porcentaje de instancias de entrenamiento válido."
        )

    if identifier == "empty_n_trees":
        return (
            gettext("Por favor, introduce un número de árboles.")
            + " "
            + gettext("Si no deseas ninguno puedes introducir 0.")
        )

    if identifier == "invalid_n_trees":
        return gettext("El número de árboles no es correcto.") + gettext(
            "Introduce un número entre 0 y 100."
        )

    if identifier == "empty_thetha":
        return gettext(
            "Por favor, introduce un número decimal en thetha"
        ) + gettext(
            "(la coma se separa mediante un punto) o 0.75 en su defecto."
        )

    if identifier == "invalid_thetha":
        return gettext("El valor de thetha no es correcto.") + gettext(
            "Introduce un número entre 0 y 1."
        )

    if identifier == "invalid_n_clss":
        return gettext(
            "Por favor, introduce un número válido de clasificadores (entre 0 y 10)."
        )

    if identifier == "check_labels_length":
        return gettext(
            "Comprueba que las etiquetas introducidas no tengan más de 63 caracteres"
        )

    return get_message("Revisa que los campos estén correctamente rellenados.")


def get_message(identifier) -> str:
    """
    Returns the message for the given identifier.
    Also translates the message to the current language.

    Args:
        identifier (str): identifier of the message
    Returns:
        str: message formatted and translated
    """
    if identifier == "successful_operation":
        return gettext("Operación realizada con éxito.")

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

    if identifier == "not_logged":
        return gettext("Debes iniciar sesión para acceder a esta página.")

    if identifier == "not_admin":
        return gettext("No tienes permisos para acceder a esta página.")

    if identifier == "false_positive_reported":
        return gettext("Falso resultado reportado correctamente.") + gettext(
            "¡Gracias por tu colaboración!"
        )

    if identifier == "model_removed":
        return gettext("Modelo eliminado correctamente.")

    if identifier == "model_updated":
        return gettext("Modelo actualizado correctamente.")

    if identifier == "models_removed":
        return gettext("Modelos eliminados correctamente.")

    if identifier == "model_not_removed":
        return gettext("No se ha podido eliminar el modelo.")

    if identifier == "model_not_updated":
        return gettext("No se ha podido actualizar el modelo.")

    if identifier == "models_not_removed":
        return gettext("No se han podido eliminar los modelos.")

    if identifier == "model_not_created":
        return gettext("No se ha podido crear el modelo.")

    if identifier == "model_not_serialized":
        return gettext("Error al serializar el modelo.")

    if identifier == "default_not_updated":
        return gettext("Error al actualizar el modelo por defecto.")

    if identifier == "model_not_selected":
        return gettext("No se ha seleccionado ningún modelo.")

    if identifier == "optimistic_scores":
        return (
            gettext(
                "¡Cuidado!, los conjuntos de entrenamiento y test tienen datos comunes."
            )
            + " "
            + gettext(
                "Los resultados de las scores podrían no ser fiables (optimistas)."
            )
        )

    if identifier == "model_stored":
        return gettext("Modelo creado y guardado correctamente.")

    if identifier == "warning_duplicates":
        return gettext(
            "Recuerda que los resultados de las scores pueden ser optimistas si el "
        ) + gettext(
            "conjunto de test contiene instancias vistas durante el entrenamiento."
        )

    if identifier == "test_success_update_db":
        return gettext(
            "Test realizado correctamente. Puedes ver los resultados en la gráfica superior."
        ) + gettext(
            "Además, se han actualizado las scores en la base de datos."
        )

    if identifier == "test_success":
        return gettext(
            "Test realizado correctamente. Puedes ver los resultados en la gráfica superior."
        )

    if identifier == "zero_scores":
        return gettext(
            "No se han podido calcular las métricas (asignado valor de 0.0): "
        )

    if identifier == "zero_scores_end":
        return gettext(". ¿Hay instancias positivas en el conjunto de test?")

    if identifier == "instance_deleted":
        return gettext("Instancia eliminada correctamente.")

    if identifier == "instance_not_deleted":
        return gettext("No se ha podido eliminar la instancia.")

    if identifier == "instances_deleted":
        return gettext("Instancias eliminadas correctamente.")

    if identifier == "instances_not_deleted":
        return gettext("No se han podido eliminar las instancias.")

    if identifier == "instance_not_selected":
        return gettext("No se ha seleccionado ninguna instancia.")

    if identifier == "instance_stored":
        return gettext("Instancia creada y guardada correctamente.")

    if identifier == "warning_check_duplicate_instance":
        return gettext(
            "Sugerencia: comprueba que no estás creando una instancia que ya existe."
        )

    if identifier == "reviews_not_selected":
        return gettext("No se han seleccionado ninguna sugerencia.")

    if identifier == "reviews_not_deleted":
        return gettext("No se han podido eliminar las sugerencias.")

    if identifier == "reviews_deleted":
        return gettext("Sugerencias eliminadas correctamente.")

    if identifier == "review_not_deleted":
        return gettext("No se ha podido eliminar la sugerencia.")

    if identifier == "url_reported":
        return gettext(
            "Tu URL ha sido reportada exitosamente. ¡Gracias por tu colaboración!"
        )

    return gettext("Mensaje no disponible. ¡Lo sentimos!")


def get_formatted_message(identifier, params=[]) -> str:
    """
    Returns the message for the given identifier and formats the params.
    Also translates the message to the current language.

    Args:
        identifier (str): identifier of the message
        params (list, optional): parameters to format the message. Defaults to [].
    Returns:
        str: message formatted and translated
    """
    if identifier == "not_callable_url":
        return (
            gettext("No se ha podido llamar ni reconstruir la URL ")
            + params[0]
            + gettext(
                ". Tampoco existe información en la base de datos acerca de ella."
            )
        )

    if identifier == "max_features":
        return gettext("Max features = ") + params[0]

    if identifier == "thetha":
        return gettext("Thetha = ") + str(params[0])[:3]

    if identifier == "n_trees":
        return gettext("Nº árboles = ") + str(params[0])

    if identifier == "n_clss":
        return gettext("Nº clasificadores = ") + str(params[0])

    if identifier == "cls_number":
        return gettext("Clasificador ") + str(params[0]) + ": " + params[1]


def get_constants_message(identifier) -> str:
    """Translates the given constant to the current language.

    Args:
        indentifier (str): constant identifier

    Returns:
        str: constant translated
    """
    if identifier == "naive_bayes_name":
        return gettext("Naive Bayes")

    if identifier == "decision_tree_name":
        return gettext("Árbol de decisión")

    if identifier == "knn_name":
        return gettext("k-vecinos más cercanos")

    if identifier == "legitimate":
        return gettext("legítimo")

    if identifier == "legitimate_upper":
        return gettext("LEGÍTIMA")

    if identifier == "phishing":
        return gettext("phishing")

    if identifier == "unavailable":
        return gettext("no disponible")

    if identifier == "no_vector":
        return gettext("no hay ningún vector generado para esta instancia")

    if identifier == "black-list":
        return gettext("lista-negra")

    if identifier == "white-list":
        return gettext("lista-blanca")

    if identifier == "auto-classified":
        return gettext("auto-clasificada")

    if identifier == "reviewed":
        return gettext("revisada")

    if identifier == "suggestion-white-list":
        return gettext("sugerencia-lista-blanca")

    if identifier == "suggestion-black-list":
        return gettext("sugerencia-lista-negra")

    if identifier == "suggestion-phishing":
        return gettext("sugerencia-phishing")

    if identifier == "suggestion-legitimate":
        return gettext("sugerencia-legítima")

    if identifier == "new-instance":
        return gettext("nueva-instancia")

    if identifier == "recommendation-review":
        return gettext("revisión-recomendada")

    if identifier == "suggestion-review-new-scanned":
        return gettext("recién-escaneada-revisar")
