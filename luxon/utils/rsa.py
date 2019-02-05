# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
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
import re
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature

from luxon.utils.encoding import (if_unicode_to_bytes,
                                  if_bytes_to_unicode)

private_key_re = re.compile(r"-----BEGIN.*PRIVATE.*-----END.*-----",
                            re.IGNORECASE | re.MULTILINE |
                            re.DOTALL)
public_key_re = re.compile(r"-----BEGIN.*PUBLIC.*-----END.*-----",
                           re.IGNORECASE | re.MULTILINE |
                           re.DOTALL)


class RSAKey(object):
    """Utility class to work with RSA keys.
    """
    def __init__(self):
        self._private_key = None
        self._public_key = None

    def generate_private_key(self, bits=4096, password=None):
        """Method to generate a private RSA key.

        Args:
            bits (int): Key bit length.
            password (str): Key password.

        Returns:
             Unicode encoded private key.
        """
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits,
            backend=default_backend()
        )

        self._public_key = None

        if password is not None:
            password = if_unicode_to_bytes(password)
            encryption_algorithm = serialization.BestAvailableEncryption(
                password
            )
        else:
            encryption_algorithm = serialization.NoEncryption()

        return if_bytes_to_unicode(self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        ))

    @property
    def public_key(self):
        """Property to return the unicode encoded RSA public key"""
        if self._public_key is None and self._private_key is None:
            raise ValueError('No Public or Private Key Loaded')

        if self._public_key is None:
            self._public_key = self._private_key.public_key()

        return if_bytes_to_unicode(self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    def load_pem_key(self, pem_key, password=None):
        """Method to load the key from string.

        Args:
            pem_key (str): Key to be loaded.
            password (str): Password for the key.
        """
        for key in private_key_re.findall(if_bytes_to_unicode(pem_key)):
            key = if_unicode_to_bytes(key)
            password = if_unicode_to_bytes(password)
            self._private_key = serialization.load_pem_private_key(
                key,
                password=password,
                backend=default_backend()
            )
            return
        for key in public_key_re.findall(if_bytes_to_unicode(pem_key)):
            key = if_unicode_to_bytes(key)
            password = if_unicode_to_bytes(password)
            self._public_key = serialization.load_pem_public_key(
                key,
                backend=default_backend()
            )
            return

        raise ValueError('Invalid PEM Key')

    def load_pem_key_file(self, file, password=None):
        """Method to load the key from string.

        Args:
            file (str): Location of file containing the key.
            password (str): Password for the key.
        """
        with open(file, 'rb') as key_file:
            self.load_pem_key(key_file.read(), password)

    def sign(self, message):
        """Method to sign a message with the Private key.

        Args:
            message (str): Message to by cryptograpically signed

        Returns:
            base64 encoded signed message.
        """
        if self._private_key is None:
            raise ValueError('No Private Key Loaded')

        message = if_unicode_to_bytes(message)
        signature = self._private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
        return if_bytes_to_unicode(base64.b64encode(signature))

    def verify(self, signature, message):
        """Method to verify the authenticity of a signed message

        Args:
            signature (str): The message's signature.
            message (str): The cleartext message that was signed and for which
                           authenticity is to be verified.
        """
        if self._public_key is None and self._private_key is None:
            raise ValueError('No Public or Private Key Loaded')

        if self._public_key is None:
            self._public_key = self._private_key.public_key()

        message = if_unicode_to_bytes(message)
        signature = base64.b64decode(signature)

        try:
            self._public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            return True
        except InvalidSignature:
            raise ValueError('RSA Verify Invalid Signature') from None

    def encrypt(self, message):
        """Method to encrypt a message with the public Key.

        Args:
            message (str): Cleartext message to be encrypted.

        Returns:
            base64 encoded encrypted message.
        """
        if self._public_key is None and self._private_key is None:
            raise ValueError('No Public or Private Key Loaded')

        if self._public_key is None:
            self._public_key = self._private_key.public_key()

        message = if_unicode_to_bytes(message)

        enc = self._public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return if_bytes_to_unicode(base64.b64encode(enc))

    def decrypt(self, message):
        """Method to decrypt a message with the private Key.

        Args:
            message (str): message encrypted wit the public key.

        Returns:
            Unicode encoded decrypted message.
        """
        if self._private_key is None:
            raise ValueError('No Private Key Loaded')

        message = base64.b64decode(message)

        dec = self._private_key.decrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return if_bytes_to_unicode(dec)
