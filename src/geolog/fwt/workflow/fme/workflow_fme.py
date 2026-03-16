from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional, TYPE_CHECKING

from ...integrace.fme.backend_base import (
    FmePozadavekSpusteni,
    FmeSpusteniVysledek,
)
from ...uloha import OnKonec, OnStart, OnZpracovaniCB, Uloha

if TYPE_CHECKING:
    from ...fwt import FWT


FmeBackendDruh = Literal["lok", "flow"]
FmeSpousteniDruh = Literal["synch", "asynch"]


@dataclass(frozen=True, slots=True)
class _FmeCil:
    backend: FmeBackendDruh
    spousteni: FmeSpousteniDruh


class _WorkflowFmeLeaf:
    """Leaf objekt: konkrétní kombinace (backend × spouštění)."""

    def __init__(self, fwt: "FWT", cil: _FmeCil):
        self._fwt = fwt
        self._cil = cil

    # ----------------------------------------------------------------------

    def spustWorkspace(
        self,
        *,
        workspace: str,
        parametry: dict[str, str],
        nazev_ulohy: str,
        on_start: OnStart = None,
        on_zpracovani: Optional[OnZpracovaniCB[str]] = None,
        on_konec: OnKonec[FmeSpusteniVysledek] = None,
    ) -> None:
        request = FmePozadavekSpusteni(
            workspace=workspace, parametry=parametry
        )
        self._fwt.workflow.fme.spustRequest(
            fme_pozadavek=request,
            backend=self._cil.backend,
            spousteni=self._cil.spousteni,
            nazev_ulohy=nazev_ulohy,
            on_start=on_start,
            on_zpracovani=on_zpracovani,
            on_konec=on_konec,
        )

    # ----------------------------------------------------------------------


class _WorkflowFmeBackend:
    """Větev backendu: `.synch` a `.asynch`."""

    def __init__(self, fwt: "FWT", backend: FmeBackendDruh):
        self.synch = _WorkflowFmeLeaf(fwt, _FmeCil(backend, "synch"))
        self.asynch = _WorkflowFmeLeaf(fwt, _FmeCil(backend, "asynch"))

    # ----------------------------------------------------------------------


class WorkflowFme:
    """
    API pro volání FME.
    """

    def __init__(self, fwt: FWT):
        self._fwt = fwt
        self.lok = _WorkflowFmeBackend(fwt, "lok")
        self.flow = _WorkflowFmeBackend(fwt, "flow")

    # ----------------------------------------------------------------------

    def spustRequest(
        self,
        *,
        fme_pozadavek: FmePozadavekSpusteni,
        backend: FmeBackendDruh,
        spousteni: FmeSpousteniDruh,
        nazev_ulohy: str,
        on_start: OnStart = None,
        on_zpracovani: Optional[OnZpracovaniCB[str]] = None,
        on_konec: OnKonec[FmeSpusteniVysledek] = None,
    ) -> None:
        """
        Spustí FME request přes framework úloh.

        Workflow zde vytváří instanci Uloha a rozhodne, zda poběží synchronně
        nebo asynchronně.

        Args:
            fme_pozadavek: Parametry požadavku na spuštění FME
            backend: Typ backendu (lokální nebo cloudový)
            spousteni: Typ spuštění (synchronní nebo asynchronní)
            nazev_ulohy: Volitelný název úlohy
            on_start: Callback pro událost startu úlohy
            on_zpracovani: Callback pro událost zpracování úlohy
            on_konec: Callback pro událost konce úlohy
        """

        def _run(
            *,
            nazev_ulohy: str,
            on_zpracovani: Optional[OnZpracovaniCB[str]] = None,
            **_: object,
        ) -> FmeSpusteniVysledek:
            return self._fwt.integrace.fme.backend(backend).spustWorkspace(
                pozadavek=fme_pozadavek,
                nazev_ulohy=nazev_ulohy,
                on_zpracovani=on_zpracovani,
            )

        uloha: Uloha[Any, FmeSpusteniVysledek, str] = Uloha(
            nazev=nazev_ulohy,
            funkce=_run,
            parametry_vstup={},
            on_start=on_start,
            on_zpracovani=on_zpracovani,
            on_konec=on_konec,
        )

        if spousteni == "synch":
            self._fwt.synch.spustUlohy([uloha])
        else:
            self._fwt.asynch.spustUlohy([uloha])

    # ----------------------------------------------------------------------
