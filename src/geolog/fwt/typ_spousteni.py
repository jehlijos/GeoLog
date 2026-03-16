from __future__ import annotations

from typing import Any, Protocol

from .uloha import Uloha


class IFwtSpoustec(Protocol):
    def spustUlohy(self, ulohy: list[Uloha[Any, Any, Any]]) -> None: ...
