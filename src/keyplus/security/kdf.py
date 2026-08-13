"""Password-based key derivation for versioned KeyPlus vaults."""

from __future__ import annotations

from dataclasses import dataclass

from argon2.low_level import Type, hash_secret_raw

from keyplus.application.errors import InvalidKDFParametersError


@dataclass(frozen=True)
class KDFParameters:
    memory_kib: int = 65_536
    iterations: int = 3
    parallelism: int = 1
    length: int = 32

    def validate(self) -> KDFParameters:
        if not 8_192 <= self.memory_kib <= 1_048_576:
            raise InvalidKDFParametersError(
                "The vault KDF memory setting is outside supported bounds."
            )
        if not 1 <= self.iterations <= 20:
            raise InvalidKDFParametersError(
                "The vault KDF iteration setting is outside supported bounds."
            )
        if not 1 <= self.parallelism <= 16:
            raise InvalidKDFParametersError(
                "The vault KDF parallelism setting is outside supported bounds."
            )
        if self.length != 32:
            raise InvalidKDFParametersError("KeyPlus vault keys must be 32 bytes.")
        return self


DEFAULT_KDF_PARAMETERS = KDFParameters()


def derive_key(password: str, salt: bytes, parameters: KDFParameters) -> bytes:
    parameters.validate()
    if not isinstance(password, str) or not password:
        raise InvalidKDFParametersError("The master password cannot be empty.")
    if len(salt) < 16:
        raise InvalidKDFParametersError("The vault KDF salt is invalid.")
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=parameters.iterations,
        memory_cost=parameters.memory_kib,
        parallelism=parameters.parallelism,
        hash_len=parameters.length,
        type=Type.ID,
    )
