"""Integrace FWT se "světem" mimo core (např. QGIS, webové služby, ...).

Core FWT (spouštění úloh) je úmyslně bez přímé vazby na QGIS.
Integrace jsou volitelné a mohou vyžadovat specifické runtime prostředí.
"""

from . import qgis

__all__: list[str] = [
    "qgis",
]
