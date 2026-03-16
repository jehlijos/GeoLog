from __future__ import annotations

"""QGIS integrace.

Pozn.: Aby se zabránilo kruhovému importu (`qgis_integrace` <-> `vrstvy`),
`VrstvyQgis` se importuje až v `QgisIntegrace.__init__` (lazy import).
"""

from ...kontext import KontextFWT
from ...utility import notNone
from .typy import TypHlaseni


class QgisIntegrace:
    """Kořenový objekt pro QGIS integraci.

    Cíl: ergonomické volání z pluginu např.
    `self.fwt.integrace.qgis.vrstvy.vytvorVrstvuSql(...)`.
    """

    def __init__(self, kontext: KontextFWT):
        self._kontext = kontext

        from .vrstvy import VrstvyQgis

        self.vrstvy = VrstvyQgis(self, kontext)

    # ----------------------------------------------------------------------

    def messageBar_text(
        self, typ_hlaseni: TypHlaseni, titul: str, zprava: str
    ) -> None:
        msg_bar = notNone(self._kontext.iface.messageBar())
        match typ_hlaseni:
            case TypHlaseni.SUCCESS:
                msg_bar.pushSuccess(titul, zprava)
            case TypHlaseni.INFO:
                msg_bar.pushInfo(titul, zprava)
            case TypHlaseni.WARNING:
                msg_bar.pushWarning(titul, zprava)
            case TypHlaseni.CRITICAL:
                msg_bar.pushCritical(titul, zprava)

    # ----------------------------------------------------------------------
