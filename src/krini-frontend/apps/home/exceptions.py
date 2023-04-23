#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   exceptions.py
@Time    :   2023/04/03 12:55:58
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

from apps.declares_messages import (
    KRINI_EXCEPTION_DEFAULT,
    KRINI_EXCEPTION_DB_DEFAULT,
    KRINI_EXCEPTION_NOT_LOGGED_DEFAULT,
)


class KriniException(Exception):
    """
    General web exception used when no action but
    to display a message to the user is required.

    Args:
        Exception (class): parent class
    """

    def __init__(self, message=KRINI_EXCEPTION_DEFAULT):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class KriniNotLoggedException(KriniException):
    """
    Used when a user tries to access a page that
    requires login.

    Args:
        Exception (class): parent class
    """

    def __init__(self, message=KRINI_EXCEPTION_NOT_LOGGED_DEFAULT):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class KriniDBException(KriniException):
    """
    Used when there is a problem with the database.

    Args:
        Exception (class): parent class
    """

    def __init__(self, message=KRINI_EXCEPTION_DB_DEFAULT):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
