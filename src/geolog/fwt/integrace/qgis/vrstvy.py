from __future__ import annotations

from typing import Optional

from pathlib import Path
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsLayerTreeLayer,
    QgsLayerTreeGroup,
    QgsDataSourceUri,
    QgsVectorFileWriter,
)

from .qgis_integrace import QgisIntegrace
from .typy import TypHlaseni

from ...kontext import KontextFWT
from ...utility import notNone
from .typ_geometrie import TypGeometrie


class VrstvyQgis:
    def __init__(self, integrace_qgis: QgisIntegrace, kontext: KontextFWT):
        self._integrace_qgis = integrace_qgis
        self._kontext = kontext
        self._projekt = notNone(QgsProject.instance())

    # ----------------------------------------------------------------------

    def vytvorVrstvuSql(
        self,
        sql_dotaz: str,
        sloupec_geom: str,
        sloupec_id: str,
        nazev_vrstvy: str,
        typ_geometrie: TypGeometrie,
        srid: int,
    ) -> QgsVectorLayer:
        """
        Vytvoří `QgsVectorLayer` z SQL dotazu.

        Args:
            sql_dotaz: SQL dotaz vracející geometrii a ID.
            sloupec_geom: Název sloupce s geometrií.
            sloupec_id: Název sloupce s ID.
            nazev_vrstvy: Název vrstvy.
            typ_geometrie: Typ geometrie (např. Point, LineString, Polygon).
            srid: SRID geometrie (např. 5514).

        Returns:
            QgsVectorLayer vytvořená z SQL dotazu.
        """
        uri = QgsDataSourceUri()
        uri.setConnection(
            self._kontext.db_konfigurace.host,
            str(self._kontext.db_konfigurace.port),
            self._kontext.db_konfigurace.databaze,
            self._kontext.db_konfigurace.jmeno,
            self._kontext.db_konfigurace.heslo,
        )
        uri.setDataSource("", f"({sql_dotaz})", sloupec_geom, "", sloupec_id)

        # Doplnění parametrů o SRID a typ geometrie
        uri_parametry = uri.uri()
        if "srid=" not in uri_parametry:
            uri_parametry += " srid=" + str(srid)
        if "type=" not in uri_parametry:
            uri_parametry += " type=" + typ_geometrie.value
        vrstva = QgsVectorLayer(
            uri_parametry, nazev_vrstvy, self._kontext.db_konfigurace.db_engine
        )

        # Kontrola vytvořené vrstvy
        isValid = vrstva.isValid()
        provider = vrstva.dataProvider()
        provider_msg = (
            provider.error().message() if provider is not None else ""
        )

        if not isValid:
            # Pozn.: u některých providerů je nejvíc informací v
            # dataProvider().error().message().
            raise RuntimeError(
                "Vrstva ze SQL dotazu není validní. "
                f"engine={self._kontext.db_konfigurace.db_engine!r}; "
                f"providerError={provider_msg!r}; "
                f"uri={uri_parametry!r}"
            )

        if provider_msg != "":
            raise RuntimeError(
                f"Chyba při načítání vrstvy ze SQL dotazu: {provider_msg}"
            )

        return vrstva

    # ----------------------------------------------------------------------

    def nastavStylVrstvy(
        self, vrstva: QgsVectorLayer, qml_soubor: str, umisteni_lokalni: bool
    ) -> None:
        """
        Nastaví styl vrstvy z QML souboru.

        Args:
            vrstva: QgsVectorLayer, kterému se má nastavit styl.
            qml_soubor: Cesta ke QML souboru se stylem.
            umisteni_lokalni: Pokud True, hledá se QML soubor v lokálním
                adresáři pluginu. Pokud False, hledá se v sdíleném adresáři.
        """
        if not qml_soubor.endswith(".qml"):
            qml_soubor += ".qml"

        adr_qml_souboru = (
            self._kontext.qml_adresar.lokalni
            if umisteni_lokalni
            else self._kontext.qml_adresar.sdileny
        )
        qml_cesta = adr_qml_souboru.joinpath(qml_soubor)

        if qml_cesta.exists():
            error_msg: str
            je_ok: bool
            error_msg, je_ok = vrstva.loadNamedStyle(str(qml_cesta))
            if je_ok:
                vrstva.triggerRepaint()
            else:
                raise RuntimeError("nastavStylVrstvy(): " + error_msg)
        else:
            self._integrace_qgis.messageBar_text(
                TypHlaseni.WARNING,
                "Chyba",
                f"QML soubor nenalezen: {qml_cesta}",
            )

    # ----------------------------------------------------------------------

    def najdiSkupinuVrstev(
        self, nazev_skupiny: str
    ) -> Optional[QgsLayerTreeGroup]:
        """
        Najde skupinu vrstev podle názvu.
        Pokud `nazev_skupiny == ""`, vrací root projektu (layerTreeRoot).

        Args:
            nazev_skupiny: Název skupiny vrstev.

        Returns:
            QgsLayerTreeGroup: Nalezená skupina vrstev nebo None pokud
            nenalezena.
        """
        root = notNone(self._projekt.layerTreeRoot())

        return root if nazev_skupiny == "" else root.findGroup(nazev_skupiny)

    # ----------------------------------------------------------------------

    def najdiZalozSkupinuVrstev(self, nazev_skupiny: str) -> QgsLayerTreeGroup:
        """
        Najde skupinu vrstev podle názvu, pokud neexistuje, založí ji.

        Args:
            nazev_skupiny: Název skupiny vrstev.

        Returns:
            QgsLayerTreeGroup: Nalezená nebo založená skupina vrstev.
        """
        skupina = self.najdiSkupinuVrstev(nazev_skupiny)
        if skupina is None:
            skupina = notNone(
                notNone(self._projekt.layerTreeRoot()).addGroup(nazev_skupiny)
            )
        return skupina

    # ----------------------------------------------------------------------

    def vlozVrstvu(
        self, skupina: QgsLayerTreeGroup, vrstva: QgsVectorLayer, poradi: int
    ) -> QgsLayerTreeLayer:
        """
        Vloží vrstvu do skupiny vrstev na požadované pořadí.

        Args:
            skupina: Skupina vrstev, do které se má vrstva vložit.
            vrstva: QgsVectorLayer, která se má vložit.
            poradi: Pořadí vrstvy ve skupině (0 = nejvýše, -1 = nejníže).

        Returns:
            QgsLayerTreeLayer: Založená vrstva ve skupině vrstev.
        """
        self._projekt.addMapLayer(vrstva, False)
        # Vložení vrstvy do skupiny na požadované pořadí
        uzel_vrstvy = notNone(skupina.insertLayer(poradi, vrstva))

        return uzel_vrstvy

    # ----------------------------------------------------------------------

    def zkopirujVrstvuDoTemp(
        self,
        vrstva: QgsVectorLayer,
        format: str = "gpkg",
        jen_vybrane: bool = False,
    ) -> str:
        """
        Zkopíruje vrstvu do TEMP a vrátí cestu k vytvořenému souboru.

        Args:
            vrstva: QgsVectorLayer, která se má zkopírovat.
            format: Formát souboru (výchozí: "gpkg", další možné: "shp",
            "geojson").
            jen_vybrane: Pokud True, kopírují se pouze vybrané prvky, jinak
            všechny.

        Returns:
            str: Cesta k vytvořenému souboru.
        """
        if not vrstva.isValid():
            raise ValueError("Neplatná vektorová vrstva")

        moznosti: QgsVectorFileWriter.SaveVectorOptions = (
            QgsVectorFileWriter.SaveVectorOptions()
        )

        moznosti.driverName = format
        moznosti.onlySelectedFeatures = jen_vybrane
        moznosti.fileEncoding = "UTF-8"
        moznosti.layerName = vrstva.name()

        idx = 0
        while True:
            temp_cesta = (
                self._kontext.temp_adresar
                + f"/temp_{vrstva.name()}_{idx}.{format}"
            )
            if not Path(temp_cesta).exists():
                break
            idx += 1

        transform_context = self._projekt.transformContext()

        kod_chyby, chybova_zprava, novy_soubor, _ = (
            QgsVectorFileWriter.writeAsVectorFormatV3(
                layer=vrstva,
                fileName=temp_cesta,
                transformContext=transform_context,
                options=moznosti,
            )
        )

        if kod_chyby != QgsVectorFileWriter.WriterError.NoError:
            raise RuntimeError(f"Chyba při zápisu vrstvy: {chybova_zprava}")

        return novy_soubor or temp_cesta  # pro jistotu

    # ----------------------------------------------------------------------
