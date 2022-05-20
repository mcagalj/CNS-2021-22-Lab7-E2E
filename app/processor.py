import typing

from .crypto import AuthenticatedEncryption, derive_key, derive_key_from_low_entropy
from .schemas import Message


class MessageProcessor:
    def __init__(
        self,
        secret: typing.Union[str, bytes, None] = None,
        username: str = None,
    ) -> None:
        self.username = username
        self.secret = secret
        self._N_out = 0

    def __str__(self):
        return f"Message processor for {self.username} ({id(self)})"

    @property
    def secret(self):
        raise AttributeError("The secret is write-only.")

    @secret.setter
    def secret(self, value: typing.Union[str, bytes, None]) -> None:
        if value is None:
            self._key = None
            self._aead = None
        elif isinstance(value, str):
            self._key = derive_key_from_low_entropy(
                length=96,
                key_seed=value,
                salt=self.username,
            )
            self._chain_key = self._key[:32]
            self._aead = AuthenticatedEncryption(self._key[32:])
        else:
            raise TypeError("The secret must be str or bytes.")

    def process_inbound(self, message: str) -> Message:
        return self._aead.decrypt(token=message)

    def process_outbound(self, message: Message) -> bytes:
        try:
            key = derive_key(
                length=96,
                key_seed=self._chain_key,
            )
            self._chain_key = key[:32]
            self._aead.key = key[32:]

            self._N_out += 1  # This should go to associated_data

            token = self._aead.encrypt(
                plaintext=message.plaintext,
                associated_data=message.associated_data,
            )
        except AttributeError:
            token = message

        return token
