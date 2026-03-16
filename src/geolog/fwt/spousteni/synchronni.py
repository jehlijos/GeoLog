from __future__ import annotations

from typing import Any, List
from ..uloha import Uloha
from ..typ_spousteni import IFwtSpoustec
from ..validace import Validace
from ..stav import StavUlohy


class SynchronniSpoustec(IFwtSpoustec):

    def spustUlohy(self, ulohy: List[Uloha[Any, Any, Any]]) -> None:
        """
        Spustí zadané úlohy synchronně, úlohy běží v hlavním vlákně QGIS GUI.

        Args:
            ulohy (List[Uloha[Any, Any, Any]]): Seznam úloh k spuštění.
        """
        Validace.validujUlohyPredSpustenim(ulohy)

        for uloha in ulohy:
            # událost on_start
            if uloha.on_start is not None:
                uloha.on_start(uloha.nazev)

            try:
                uloha.vysledek = uloha.funkce(
                    **uloha.parametry_vstup,
                    nazev_ulohy=uloha.nazev,
                    on_zpracovani=uloha.on_zpracovani,
                )
                uloha.stav = StavUlohy.OK
                uloha.vyjimka = None
            except Exception as e:
                uloha.vysledek = None
                uloha.stav = StavUlohy.CHYBA
                uloha.vyjimka = e

            # událost on_konec
            if uloha.on_konec is not None:
                uloha.on_konec(
                    uloha.nazev, uloha.stav, uloha.vysledek, uloha.vyjimka
                )

    # ----------------------------------------------------------------------
