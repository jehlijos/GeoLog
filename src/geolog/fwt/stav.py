from __future__ import annotations

from enum import Enum


class StavUlohy(str, Enum):
    """Stav zpracování úlohy.

    Používá se místo textových hodnot jako "OK" / "CHYBA".
    Dědí ze str kvůli snadnému logování/serializaci.
    """

    OK = "OK"
    CHYBA = "CHYBA"


# ----------------------------------------------------------------------
