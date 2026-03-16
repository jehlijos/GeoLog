from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from ...integrace.qgis.typ_geometrie import TypGeometrie


if TYPE_CHECKING:
    from ...fwt import FWT


class WorkflowQgis:
    def __init__(self, fwt: FWT):
        self._fwt = fwt
        self._qgis_vrstvy = self._fwt.integrace.qgis.vrstvy

    # ----------------------------------------------------------------------

    def vytvorVrstvuSql(
        self,
        sql_dotaz: str,
        sloupec_geom: str,
        sloupec_id: str,
        qml_soubor_styl: Optional[str],
        umisteni_lokalni: Optional[bool],
        nazev_vrstvy: str,
        nazev_skupiny: str,
        poradi: int = -1,
        typ_geometrie: TypGeometrie = TypGeometrie.LineString,
        srid: int = 5514,
        rozbalit: Optional[bool] = None,
    ) -> None:
        """
        Vytvoří SQL vrstvu z dotazu, případně nastaví styl, a vloží
        do projektu.

        Args:
            sql_dotaz: SQL dotaz vracející geometrii a ID.
            sloupec_geom: Název sloupce s geometrií.
            sloupec_id: Název sloupce s ID.
            qml_soubor_styl: Cesta ke QML souboru pro styl (může být None
                pro výchozí styl).
            umisteni_lokalni: True pokud je cesta ke QML souboru lokální,
                False pokud je vzdálená na serveru (může být None, pak se
                neuplatní žádná změna).
            nazev_vrstvy: Název vrstvy, jak se zobrazí v QGIS.
            nazev_skupiny: Název skupiny vrstev, do které se má vrstva vložit
                (prázdný string pro root).
            poradi: Pořadí vrstvy ve skupině (výchozí -1 pro přidání na konec).
            typ_geometrie: Typ geometrie (např. Point, LineString, Polygon).
            srid: SRID geometrie (např. 5514).
            rozbalit: True pro rozbalení vrstvy ve stromu vrstev, False
                pro sbalení, None pro žádnou změnu.

        Returns:
            None
        """
        # Vytvoření SQL vrstvy
        vrstva = self._qgis_vrstvy.vytvorVrstvuSql(
            sql_dotaz,
            sloupec_geom,
            sloupec_id,
            nazev_vrstvy,
            typ_geometrie,
            srid,
        )
        # Nastavení stylu vrstvě
        if qml_soubor_styl is not None and umisteni_lokalni is not None:
            self._qgis_vrstvy.nastavStylVrstvy(
                vrstva, qml_soubor_styl, umisteni_lokalni
            )
        # Nalezení skupiny vrstev, do které bude potřeba vrstvu vložit
        skupina = self._qgis_vrstvy.najdiZalozSkupinuVrstev(nazev_skupiny)
        # Přidání vrstvy do skupiny vrstev na požadované pořadí
        uzel_vrstvy = self._qgis_vrstvy.vlozVrstvu(skupina, vrstva, poradi)
        # Rozbalení/sbalení vrstvy
        if rozbalit is not None:
            uzel_vrstvy.setExpanded(rozbalit)

    # ----------------------------------------------------------------------
