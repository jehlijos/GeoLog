from __future__ import annotations

import inspect
from typing import Any, Iterable

from .uloha import Uloha


class ChybaValidaceUlohy(TypeError):
    """
    Chyba vyvolaná při validaci úlohy (nesoulad signatury funkce a parametrů).
    """


# ----------------------------------------------------------------------


class Validace:
    @staticmethod
    def validujUlohyPredSpustenim(
        ulohy: Iterable[Uloha[Any, Any, Any]],
    ) -> None:
        """Provede validaci všech úloh ještě před spuštěním první z nich.

        Kontroluje hlavně:
        - že `uloha.funkce` lze zavolat s `**uloha.parametry_vstup` a
            s keyword parametrem `on_zpracovani`
        - že funkce podporuje keyword-only / keyword argument `on_zpracovani`
            (povinné dle konvence frameworku)

        Vyvolá `ChybaValidaceUlohy` při první chybě.

        Args:
            ulohy (Iterable[Uloha[Any, Any]]): Seznam úloh k validaci.

        Raises:
            ChybaValidaceUlohy: Při chybě validace.
        """

        for uloha in ulohy:
            Validace._validujJednuUlohu(uloha)

    # ----------------------------------------------------------------------

    @staticmethod
    def _validujJednuUlohu(uloha: Uloha[Any, Any, Any]) -> None:
        """
        Provede validaci jedné úlohy.

        Args:
            uloha (Uloha[Any, Any]): Úloha k validaci.

        Raises:
            ChybaValidaceUlohy: Při chybě validace.
        """
        funkce = uloha.funkce

        # 1) Signatura funkce a přítomnost parametrů, které framework injektuje
        try:
            sig = inspect.signature(funkce)
        except (TypeError, ValueError) as e:
            raise ChybaValidaceUlohy(
                f"Uloha '{uloha.nazev}': nelze získat signaturu funkce "
                f"{funkce!r}: {e}"
            ) from e

        params = sig.parameters
        ma_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
        )

        if not ("nazev_ulohy" in params or ma_kwargs):
            raise ChybaValidaceUlohy(
                f"Uloha '{uloha.nazev}': funkce "
                f"'{Validace._jmenoFunkce(funkce)}' musí mít parametr "
                "'nazev_ulohy' (např. nazev_ulohy: str)."
            )

        if not ("on_zpracovani" in params or ma_kwargs):
            raise ChybaValidaceUlohy(
                f"Uloha '{uloha.nazev}': funkce "
                f"'{Validace._jmenoFunkce(funkce)}' musí mít parametr "
                "'on_zpracovani' (např. on_zpracovani: OnZpracovaniCB | "
                "None = None)."
            )

        # 2) Validace volatelnosti s parametry (nejdůležitější pro odhalení
        #   'unexpected keyword argument ...')
        call_kwargs: dict[str, Any] = dict(uloha.parametry_vstup)
        call_kwargs["nazev_ulohy"] = uloha.nazev
        call_kwargs["on_zpracovani"] = uloha.on_zpracovani

        try:
            sig.bind_partial(**call_kwargs)
        except TypeError as e:
            raise ChybaValidaceUlohy(
                f"Uloha '{uloha.nazev}': parametry_vstup neodpovídají "
                f"signatuře funkce '{Validace._jmenoFunkce(funkce)}'. "
                f"Chyba: {e}. Parametry: "
                f"{sorted(uloha.parametry_vstup.keys())}"
            ) from e

        # 3) Volitelná kontrola typu callbacku on_zpracovani
        if uloha.on_zpracovani is not None and not callable(
            uloha.on_zpracovani
        ):
            raise ChybaValidaceUlohy(
                f"Uloha '{uloha.nazev}': on_zpracovani musí být callable, "
                f"ale je {type(uloha.on_zpracovani)!r}."
            )

    # ----------------------------------------------------------------------

    @staticmethod
    def _jmenoFunkce(funkce: Any) -> str:
        """
        Vrátí jméno funkce včetně jejího kontextu (např. "modul.funkce").

        Args:
            funkce (Any): Funkce, jejíž jméno chceme získat.

        Returns:
            str: Jméno funkce včetně kontextu.
        """
        return getattr(
            funkce, "__qualname__", getattr(funkce, "__name__", repr(funkce))
        )

    # ----------------------------------------------------------------------
