"""Domain models stored inside an encrypted KeyPlus vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .errors import CorruptVaultError, ValidationError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} cannot be empty.")
    return value.strip()


def _required_secret(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} cannot be empty.")
    return value


@dataclass(frozen=True)
class EntryDraft:
    name: str
    domain: str
    password: str

    def validated(self) -> EntryDraft:
        return EntryDraft(
            _required_text(self.name, "Entry name"),
            _required_text(self.domain, "Domain"),
            _required_secret(self.password, "Password"),
        )


@dataclass(frozen=True)
class EntryChanges:
    name: str | None = None
    domain: str | None = None
    password: str | None = None

    def apply(self, entry: VaultEntry, now: str) -> VaultEntry:
        if self.name is None and self.domain is None and self.password is None:
            raise ValidationError("At least one entry field must be changed.")
        return VaultEntry(
            id=entry.id,
            name=_required_text(self.name, "Entry name")
            if self.name is not None
            else entry.name,
            domain=_required_text(self.domain, "Domain")
            if self.domain is not None
            else entry.domain,
            password=_required_secret(self.password, "Password")
            if self.password is not None
            else entry.password,
            created_at=entry.created_at,
            updated_at=now,
        )


@dataclass(frozen=True)
class VaultEntry:
    id: str
    name: str
    domain: str
    password: str
    created_at: str
    updated_at: str

    @classmethod
    def create(
        cls, draft: EntryDraft, *, now: str, entry_id: str | None = None
    ) -> VaultEntry:
        clean = draft.validated()
        return cls(
            entry_id or str(uuid4()), clean.name, clean.domain, clean.password, now, now
        )

    @classmethod
    def from_dict(cls, value: Any) -> VaultEntry:
        try:
            entry = cls(
                id=str(value["id"]),
                name=str(value["name"]),
                domain=str(value["domain"]),
                password=str(value["password"]),
                created_at=str(value["created_at"]),
                updated_at=str(value["updated_at"]),
            )
            EntryDraft(entry.name, entry.domain, entry.password).validated()
            if not entry.id or not entry.created_at or not entry.updated_at:
                raise ValueError("missing entry metadata")
            return entry
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            raise CorruptVaultError(
                "The vault contains an invalid entry record."
            ) from exc

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "password": self.password,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class VaultDocument:
    created_at: str
    updated_at: str
    entries: list[VaultEntry] = field(default_factory=list)
    payload_version: int = 1

    @classmethod
    def empty(cls, *, now: str | None = None) -> VaultDocument:
        timestamp = now or utc_now()
        return cls(timestamp, timestamp, [])

    @classmethod
    def from_dict(cls, value: Any) -> VaultDocument:
        try:
            if value.get("payload_version") != 1:
                raise CorruptVaultError("The vault payload version is invalid.")
            entries = [VaultEntry.from_dict(item) for item in value["entries"]]
            created = str(value["created_at"])
            updated = str(value["updated_at"])
            if not created or not updated:
                raise ValueError("missing vault timestamps")
            return cls(created, updated, entries)
        except CorruptVaultError:
            raise
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise CorruptVaultError("The decrypted vault payload is invalid.") from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "payload_version": self.payload_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }
