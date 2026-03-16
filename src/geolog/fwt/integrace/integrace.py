from __future__ import annotations

from ..kontext import KontextFWT
from .qgis.qgis_integrace import QgisIntegrace
from .fme.fme_integrace import FmeIntegrace


class Integrace:
    """Kořenový objekt pro všechny integrace frameworku.

    Účel: držet závislosti (např. KontextFWT) a poskytovat konzistentní přístup
    jako `fwt.integrace.qgis...`.
    """

    def __init__(self, kontext: KontextFWT):
        # self._kontext = kontext
        self.qgis = QgisIntegrace(kontext)
        self.fme = FmeIntegrace(kontext)

    # ----------------------------------------------------------------------
