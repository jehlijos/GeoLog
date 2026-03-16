from __future__ import annotations

from typing import List, Any, TYPE_CHECKING, TypeAlias
import time

from ..fwt import FWT, StavUlohy
from ..fwt.uloha import OnZpracovaniCB, Uloha
from ..fwt.validace import ChybaValidaceUlohy

if TYPE_CHECKING:
    from ..topas_vyvoj_1_dialog import TopasVyvoj1Dialog

# Typový alias parametrů handleru on_zpracovani (progress callback)
ParOnZpracFunkce1: TypeAlias = tuple[float, str]


class SpusteniFunkce1:
    def __init__(self, fwt: FWT, okno: "TopasVyvoj1Dialog"):
        """
        Inicializace třídy pro spuštění funkce 1.

        Args:
            fwt: Instance FWT pro správu úloh.
            okno: Instance dialogu pro uživatelské rozhraní.
        """
        self.fwt = fwt
        self.okno = okno

    # ----------------------------------------------------------------------

    def spustFunkci1(self, synchronne: bool) -> None:
        """
        Zajistí spuštění funkce 1.

        Args:
            synchronne: Příznak, zda funkci 1 spustit synchronně nebo
                asynchronně.
        """

        def nastavUlohy(
            nazev_ulohy: str,
        ) -> List[Uloha[Any, str, ParOnZpracFunkce1]]:
            """
            Pomocná funkce pro nastavení úloh pro zpracování.

            Args:
                nazev_ulohy: Název úlohy.

            Returns:
                List[Uloha[Any, str, ParametryZpracovaniFunkce1]]: Seznam
                    úloh ke spuštění.
            """
            ulohy: List[Uloha[Any, str, ParOnZpracFunkce1]] = []

            for i in range(1, 9):
                parametry: dict[str, Any] = {"par_1": i, "par_2": "test str"}
                uloha: Uloha[Any, str, ParOnZpracFunkce1] = Uloha(
                    nazev=nazev_ulohy,
                    funkce=funkce1,
                    parametry_vstup=parametry,
                    on_start=funkce1_onStart,
                    on_zpracovani=funkce1_onZpracovani,
                    on_konec=funkce1_onKonec,
                )
                ulohy.append(uloha)

            return ulohy

        def funkce1(
            *,
            nazev_ulohy: str,
            par_1: int,
            par_2: str,
            on_zpracovani: OnZpracovaniCB[ParOnZpracFunkce1] | None = None,
        ) -> str:
            """
            Hlavní výkonná funkce, která něco dělá.
            """
            time.sleep(2)

            if on_zpracovani is not None:
                on_zpracovani(nazev_ulohy, (50.0, "Zpracovávám..."))

            time.sleep(2)

            return f"Výsledek funkce 1: {par_1}, {par_2}"

        # ----------------------------------------------------------------------

        def funkce1_onStart(nazev_ulohy: str) -> None:
            """Callback pro start úlohy (OnStart)."""
            self.okno.Vystup_1.appendPlainText(f"[{nazev_ulohy}] start úlohy")

        # ----------------------------------------------------------------------

        def funkce1_onZpracovani(
            nazev_ulohy: str, parametry: ParOnZpracFunkce1
        ) -> None:
            """Callback pro průběh zpracování (OnZpracovaniCB)."""
            progress, zprava = parametry
            self.okno.Vystup_1.appendPlainText(
                f"[{nazev_ulohy}] {progress:.0f}% - {zprava}"
            )

        # ----------------------------------------------------------------------

        def funkce1_onKonec(
            nazev_ulohy: str,
            stav: StavUlohy,
            vysledek: str | None,
            vyjimka: Exception | None,
        ) -> None:
            """Callback pro konec úlohy (OnKonec)."""
            if stav == StavUlohy.OK:
                self.okno.Vystup_1.appendPlainText(
                    f"[{nazev_ulohy}] úspěch, výsledek: {vysledek}"
                )
            else:
                self.okno.Vystup_1.appendPlainText(
                    f"[{nazev_ulohy}] chyba, výjimka: {vyjimka}"
                )

        # ----------------------------------------------------------------------

        try:
            if synchronne:
                ulohy = nastavUlohy("Test S")
                self.fwt.synch.spustUlohy(ulohy)
            else:
                ulohy = nastavUlohy("Test A")
                self.fwt.asynch.spustUlohy(ulohy)
        except ChybaValidaceUlohy as e:
            self.okno.Vystup_1.appendPlainText(f"CHYBA validace úlohy: {e}")

    # ----------------------------------------------------------------------
