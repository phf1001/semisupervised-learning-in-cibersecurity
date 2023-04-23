#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   models.py
@Time    :   2023/03/30
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es

Copyright (c) 2019 - present AppSeed.us
Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/
"""

import os
import hashlib
import binascii


def hash_pass(password):
    """
    Hash a password for storing. Return bytes.

    Args:
        password (str): password to hash

    Returns:
        bytes: encoded password
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt, 100000
    )
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash


def verify_pass(provided_password, stored_password):
    """
    Verify a stored password against one provided by user

    Args:
        provided_password (str): password provided by user
        stored_password (bytes): stored password (in database)
    Returns:
        bool: True if password is correct, False otherwise
    """
    stored_password = stored_password.decode("ascii")
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512",
        provided_password.encode("utf-8"),
        salt.encode("ascii"),
        100000,
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password
