from __future__ import annotations
from logging import config
import yaml

from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias

from ..fwt import FWT, StavUlohy

from ..fwt.integrace.qgis.typy import TypHlaseni
from ..fwt.integrace.fme.backend_base import (
    FmePozadavekSpusteni,
    FmeSpusteniVysledek,
)

from .nacteni_fme_paramteru import NacteniFmeParametru

if TYPE_CHECKING:
    from ..topas_vyvoj_1_dialog import TopasVyvoj1Dialog


# Typový alias parametrů handleru on_zpracovani pro FME (řádek logu)
ParOnZpracFmeLok: TypeAlias = str


class SpusteniFmeLok:
    """Spouštění lokálního FME Workbench přes FWT (synch/asynch)."""

    def __init__(self, fwt: FWT, okno: "TopasVyvoj1Dialog"):
        self._fwt = fwt
        self._okno = okno

    # ------------------------------------------------------------------

    def spustFme1(
        self,
        synchronne: bool,
        lokalni: None,
        qgis_layer_name: str = "",
    ) -> None:
        """Spustí FME workspace jako úlohu přes workflow (lokální/sdílený)."""
        from qgis.core import QgsProject, QgsVectorLayer
        from qgis.PyQt.QtCore import QTimer

        # -----------------------------
        # Bezpečný výpis do UI (i když callback běží mimo UI thread)
        def ui_log(text: str) -> None:
            QTimer.singleShot(
                0, lambda: self._okno.Vystup_1.appendPlainText(text)
            )

        # Název FME z UI.
        nazev_FME_souboru = self._okno.leFmeSoubor.text().strip()

        # Získání parametrů z FME_config.yaml podle názvu FME souboru
        nacteni_parametru = NacteniFmeParametru(nazev_FME_souboru) 
        volitelne_parametry,format_vystupu, je_lokalni, nazev_vystup = nacteni_parametru.nacti_parametry()

        if lokalni is None:
            lokalni = je_lokalni


        # Zajistíme unikátní název výstupního souboru v temp adresáři, aby
        # nedošlo k přepsání existujícího.
        idx = 0
        while True:
            temp_vystup = Path(self._fwt.kontext.temp_adresar).joinpath(
                f"{nazev_vystup}_{idx}.{format_vystupu}"
            )
            if not temp_vystup.exists():
                break
            idx += 1

        # Zajistime existenci cilove slozky pred spustenim FME.
        temp_vystup.parent.mkdir(parents=True, exist_ok=True)

        # -----------------------------
        def fme_onStart(nazev_ulohy: str) -> None:
            ui_log(f"[{nazev_ulohy}] start")

        # -----------------------------
        def fme_onZpracovani(
            nazev_ulohy: str, parametry: ParOnZpracFmeLok
        ) -> None:
            ui_log(f"[{nazev_ulohy}] {parametry}")

        # -----------------------------
        def fme_onKonec(
            nazev_ulohy: str,
            stav: StavUlohy,
            vysledek: FmeSpusteniVysledek | None,
            vyjimka: Exception | None,
        ) -> None:
            if stav != StavUlohy.OK:
                msg = (
                    str(vyjimka) if vyjimka else "Neznámá chyba (bez výjimky)."
                )
                ui_log(f"[{nazev_ulohy}] CHYBA: {msg}")
                self._fwt.integrace.qgis.messageBar_text(
                    TypHlaseni.CRITICAL,
                    "TOPAS",
                    f"[{nazev_ulohy}] CHYBA: {msg}",
                )
                return

            ui_log(f"[{nazev_ulohy}] konec")
            # Zobraz message bar přes existující logiku
            self._fwt.integrace.qgis.messageBar_text(
                TypHlaseni.SUCCESS,
                "TOPAS",
                "FME úloha byla úspěšně dokončena.",
            )

            if not temp_vystup.exists():
                ui_log(f"Výstupní soubor nenalezen: {temp_vystup}")
                return

            vrstva_out = QgsVectorLayer(str(temp_vystup), "Výstup FME", "ogr")
            if not vrstva_out.isValid():
                ui_log(f"Výstupní vrstva není validní: {temp_vystup}")
                return

            vrstvy = self._fwt.integrace.qgis.vrstvy

            # --- Skupina vrstev z UI (pokud existuje) ---
            nazev_skupiny = (
                self._okno.VstupSkupina_1.currentText()
                if hasattr(self._okno, "VstupSkupina_1")
                else None
            )

            #  Ošetření Optional návratu instance()
            projekt = QgsProject.instance()
            if projekt is None:
                ui_log(
                    "Projekt není dostupný. "
                    "(QgsProject.instance() vrátil None.)"
                )
                return

            # Při přidání do QGIS změň název vrstvy podle parametru
            layer_name = qgis_layer_name if qgis_layer_name else nazev_vystup
            if not nazev_skupiny or nazev_skupiny == "(bez skupiny)":
                projekt.addMapLayer(vrstva_out, True)
                vrstvy_qgis = projekt.mapLayersByName(vrstva_out.name())
                if vrstvy_qgis:
                    vrstvy_qgis[0].setName(layer_name)
            else:
                skupina = vrstvy.najdiZalozSkupinuVrstev(nazev_skupiny or "")
                vrstvy.vlozVrstvu(skupina, vrstva_out, -1)
                lyr = skupina.findLayer(vrstva_out.id())
                if lyr is not None:
                    lyr.setName(layer_name)

            ui_log(f"Výstupní vrstva načtena: {temp_vystup}")

            # --- Nastavení stylu vrstvy podle QML ---
            qml_soubor = self._okno.leQmlSoubor.text().strip()
            umisteni_lokalni = (
                self._okno.chbLokalniQml.isChecked()
                if hasattr(self._okno, "chbLokalniQml")
                else True
            )

            if qml_soubor:
                try:
                    vrstvy.nastavStylVrstvy(
                        vrstva_out, qml_soubor, umisteni_lokalni
                    )
                except Exception as e:
                    ui_log(f"CHYBA při nastavování stylu: {e}")

        # ------------------------------------------------------------------
        # --- Získání vybrané vrstvy z Vstup_1 a kopie do TEMP ---
        projekt = QgsProject.instance()
        if projekt is None:
            ui_log(
                "Projekt není dostupný. "
                "(QgsProject.instance() vrátil None.)"
            )
            return

        vrstvy_map = projekt.mapLayers()
        vstup_id = self._okno.Vstup_1.currentData()
        vrstva_in = vrstvy_map.get(vstup_id) if vstup_id else None

        if not isinstance(vrstva_in, QgsVectorLayer):
            ui_log("Vybraná vrstva není vektorová nebo není vybrána.")
            return

        jen_vybrane = self._okno.chbPouzeVybrane.isChecked()
        temp_cesta = self._fwt.integrace.qgis.vrstvy.zkopirujVrstvuDoTemp(
            vrstva_in, format_vystupu, jen_vybrane
        )

        # --- Výběr workspace zachován podle uživatele ---

        if lokalni:
            ws = str(self._fwt.kontext.fme_adresar.lokalni) + "/" + nazev_FME_souboru
        else:
            ws = str(self._fwt.kontext.fme_adresar.sdileny) + "/" + nazev_FME_souboru

        # Spojení základních a volitelných parametrů pro FME
        parametry_fme = {
            "VSTUP_GPKG": str(temp_cesta),
            "VYSTUP_SOUBOR": str(temp_vystup),
        }

        vstupni_parametry = {**parametry_fme, **volitelne_parametry}

        # Vytvoření požadavku pro spuštění FME s parametry
        pozadavek = FmePozadavekSpusteni(
            workspace=ws,
            parametry= vstupni_parametry
        )

        spousteni = "synch" if synchronne else "asynch"
        self._fwt.workflow.fme.spustRequest(
            fme_pozadavek=pozadavek,
            backend="lok",
            spousteni=spousteni,
            nazev_ulohy="FME 2 " + ("S" if synchronne else "A"),
            on_start=fme_onStart,
            on_zpracovani=fme_onZpracovani,
            on_konec=fme_onKonec,
        )

    # ------------------------------------------------------------------
