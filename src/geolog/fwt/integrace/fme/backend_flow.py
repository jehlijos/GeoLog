from __future__ import annotations

from typing import final, Optional

from ...kontext import KontextFWT
from ...uloha import OnZpracovaniCB
from .backend_base import FmePozadavekSpusteni, FmeSpusteniVysledek


@final
class FmeFlowBackend:
    def __init__(self, kontext: KontextFWT):
        self._kontext = kontext

    # ----------------------------------------------------------------------

    def spustWorkspace(
        self,
        *,
        pozadavek: FmePozadavekSpusteni,
        nazev_ulohy: str,
        on_zpracovani: Optional[OnZpracovaniCB[str]] = None,
        timeout_s: float = 90.0,
    ) -> FmeSpusteniVysledek:
        # implementace spouštění přes FME Flow (REST)
        raise NotImplementedError(
            "Spouštění FME procesů přes FME Flow není zatím implementováno."
        )

    # ----------------------------------------------------------------------
