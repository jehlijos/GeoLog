from __future__ import annotations

from typing import Any, List
from concurrent.futures import ThreadPoolExecutor
from ..uloha import Uloha
from ..typ_spousteni import IFwtSpoustec
from ..threading.callback_wrapper import CallbackWrapper
from ..validace import Validace
from ..stav import StavUlohy


class AsynchronniSpoustec(IFwtSpoustec):

    def __init__(self, executor: ThreadPoolExecutor, wrapper: CallbackWrapper):
        self._executor: ThreadPoolExecutor = executor
        self._wrapper: CallbackWrapper = wrapper

    # ----------------------------------------------------------------------

    def spustUlohy(self, ulohy: List[Uloha[Any, Any, Any]]) -> None:
        """
        Spustí zadané úlohy asynchronně pomocí ThreadPoolExecutoru.

        Args:
            ulohy (List[Uloha[Any, Any, Any]]): Seznam úloh k spuštění.
        """
        Validace.validujUlohyPredSpustenim(ulohy)

        for uloha in ulohy:
            self._obalCallbacky(uloha)
            self._executor.submit(self._spustJednuUlohu, uloha)

    # ----------------------------------------------------------------------

    def _obalCallbacky(self, uloha: Uloha[Any, Any, Any]) -> None:
        """
        Obalí callbacky (handlery událostí úlohy on_start, on_zpracovani,
        on_konec) tak, aby byly volány v hlavním vlákně QGIS GUI.

        Args:
            uloha (Uloha[Any, Any, Any]): Úloha, jejíž callbacky budou obaleny.
        """
        uloha.on_start = self._wrapper.wrap(uloha.on_start)
        uloha.on_zpracovani = self._wrapper.wrap(uloha.on_zpracovani)
        uloha.on_konec = self._wrapper.wrap(uloha.on_konec)

    # ----------------------------------------------------------------------

    def _spustJednuUlohu(self, uloha: Uloha[Any, Any, Any]) -> None:
        """
        Spustí asynchronně jednu úlohu a zpracuje její výsledky a výjimky.

        Args:
            uloha (Uloha[Any, Any, Any]): Úloha k provedení.
        """
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
