#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   exceptions.py
@Time    :   2023/04/03 10:00:58
@Author  :   Patricia Hernando Fernández 
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
"""

from apps.messages import get_exception_message


class KriniException(Exception):
    """
    General web exception used when no action but
    to display a message to the user is required.

    Args:
        Exception (class): parent class
    """

    def __init__(
        self, message=get_exception_message("krini_exception_default")
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class KriniSSLException(KriniException):
    """
    Used when a URL has certificate problems.

    Args:
        Exception (class): parent class
    """

    def __init__(
        self,
        message=get_exception_message("krini_SSL_exception_default"),
    ):
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

    def __init__(
        self,
        message=get_exception_message("krini_not_logged_exception_default"),
    ):
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

    def __init__(
        self, message=get_exception_message("krini_db_exception_default")
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
