"""Αναγνωριστικό αιτήματος για συσχέτιση HTTP, σφαλμάτων και ιστορικού."""

from contextvars import ContextVar

id_trexontos_aitimatos: ContextVar[str | None] = ContextVar("id_aitimatos", default=None)
