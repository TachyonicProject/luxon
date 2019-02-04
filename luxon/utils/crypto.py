# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan, Dave Kruger.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
import os
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from math import floor

from luxon.utils.encoding import (if_unicode_to_bytes,
                                  if_bytes_to_unicode)


class Crypto(object):
    """Utility class to work with cryptography symmetrical keys.

    Args:
        algorithm (obj): a cryptography.hazmat.primitives.ciphers.algorithms
                         algorithm
        modes (obj): a cryptography.hazmat.primitives.ciphers.modes object
        backend (obj): a cryptography.hazmat.backends backend obj.
        pad (obj): a a cryptography.hazmat.primitives.padding scheme object.
    """

    def __init__(self, algorithm=algorithms.AES, modes=modes.CBC,
                 backend=default_backend(), pad=padding.PKCS7):
        self._key = None
        self._iv = None
        self._algorithm = algorithm
        self._modes = modes
        self._backend = backend
        self._padding = pad(algorithm.block_size)

    def generate_key(self, bits=32*8):
        """Method to generate a symmetrical key.

        Args:
            bits (int): Key bit length.

        Returns:
             Binary encoded private key.
        """
        self._key = os.urandom(floor(bits/8))
        return self._key

    def generate_iv(self, bits=16*8):
        """Method to generate a initialization vector.

        Args:
            bits (int): vector bit length.

        Returns:
             Binary initialization vector.
        """
        self._iv = os.urandom(floor(bits/8))

        return self._iv

    @property
    def key(self):
        """Property to return the binary key"""
        if self._key is None:
            raise ValueError('No Key Loaded')

        return self._key

    @property
    def iv(self):
        """Property to return the unicode encoded key"""
        if self._iv is None:
            raise ValueError('No Initialization Vector Loaded')

        return self._iv

    def load_key(self, key):
        """Method to load the binary key.

        Args:
            key (str): Key to be loaded.
        """
        self._key = key

    def load_iv(self, iv):
        """Method to load the initialization vector from binary.

        Args:
            iv (str): Initialization vector to be loaded.
        """
        self._iv = if_unicode_to_bytes(iv)

    def load_key_file(self, file):
        """Method to load the key from file.

        Args:
            file (str): Location of file containing the key.
            """
        with open(file, 'rb') as key_file:
            self.load_key(key_file.read())

    def load_iv_file(self, file):
        """Method to load the initialization vector from file.

        Args:
            file (str): Location of file containing the initialization vector.
            """
        with open(file, 'rb') as iv_file:
            self.load_iv(iv_file.read())

    def encrypt(self, message):
        """Method to encrypt a message with the symmetric Key.

        Args:
            message (str): Cleartext message to be encrypted.

        Returns:
            base64 encoded encrypted message.
        """
        if self._key is None and self._iv is None:
            raise ValueError('No Key and Initialization vector Loaded')

        _padder = self._padding.padder()
        message = if_unicode_to_bytes(message)
        padded_data = _padder.update(message) + _padder.finalize()

        _cipher = Cipher(self._algorithm(self._key),
                         self._modes(self._iv), backend=self._backend)

        _encryptor = _cipher.encryptor()

        _ct = _encryptor.update(padded_data) + _encryptor.finalize()

        return if_bytes_to_unicode(base64.b64encode(_ct))

    def decrypt(self, message):
        """Method to decrypt a message with the secret Key.

        Args:
            message (str): message encrypted with the secret key.

        Returns:
            Unicode encoded decrypted message.
        """
        if self._key is None and self._iv is None:
            raise ValueError('No Key and Initialization vector Loaded')

        _unpadder = self._padding.unpadder()
        _cipher = Cipher(self._algorithm(self._key),
                         self._modes(self._iv), backend=self._backend)

        message = base64.b64decode(message)

        _decryptor = _cipher.decryptor()

        _cleartext = _decryptor.update(message) + _decryptor.finalize()

        return if_bytes_to_unicode(
            _unpadder.update(_cleartext) + _unpadder.finalize())
