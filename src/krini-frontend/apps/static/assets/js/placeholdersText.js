function myGettext($id) {
    return vsprintf(gettext($id), array_slice(func_get_args(), 1));
}