from __future__ import annotations

from typing import Literal

from ...kontext import KontextFWT
from .backend_lok import FmeLokBackend
from .backend_flow import FmeFlowBackend


FmeBackendKind = Literal["lok", "flow"]
FmeBackend = FmeLokBackend | FmeFlowBackend


class FmeIntegrace:
    def __init__(self, kontext: KontextFWT):
        # self._kontext = kontext
        self._lok = FmeLokBackend(kontext)
        self._flow = FmeFlowBackend(kontext)

    # ----------------------------------------------------------------------

    def backend(self, kind: FmeBackendKind = "lok") -> FmeBackend:
        """Vrátí backend dle typu.

        `lok` = lokální FME (Engine/CLI)
        `flow` = FME Flow (REST)

        Args:
            kind: Typ backendu (výchozí: `lok`).

        Returns:
            Instance požadovaného backendu.

        Raises:
            ValueError: Pokud je zadán neznámý typ backendu.
        """
        if kind == "lok":
            return self._lok
        if kind == "flow":
            return self._flow
        raise ValueError(f"Neznámý FME backend: {kind!r}")  # Pro jistotu

    # ----------------------------------------------------------------------
