from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


# Společný typ výsledku spuštění FME workspace.
# (úspěch, zpráva/log, exit code)
FmeSpusteniVysledek: TypeAlias = tuple[bool, str, int]


@dataclass(frozen=True, slots=True)
class FmePozadavekSpusteni:
    """
    Kolekce parametrů požadavku na spuštění FME workspace.

    Attributes:
        workspace (str): Cesta k FME workspace (.fmw).
        parametry (dict[str, str]): Slovník parametrů předávaných
            do FME workspace.
    """

    workspace: str
    parametry: dict[str, str]


# ----------------------------------------------------------------------
