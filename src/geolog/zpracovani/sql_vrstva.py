from ..fwt import FWT, StavUlohy
from ..fwt.uloha import OnZpracovaniCB, Uloha
from ..fwt.validace import ChybaValidaceUlohy

from ..fwt.integrace.qgis.typy import TypHlaseni
from ..fwt.integrace.qgis.vrstvy import TypGeometrie

from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..topas_vyvoj_1_dialog import TopasVyvoj1Dialog


class SqlVrstva:
    def __init__(self, fwt: FWT, okno: "TopasVyvoj1Dialog"):
        """
        Inicializace třídy pro spuštění funkce 1.

        Args:
            fwt: Instance FWT pro správu úloh.
            okno: Instance dialogu pro uživatelské rozhraní.
        """
        self._fwt = fwt
        self._okno = okno

    # ----------------------------------------------------------------------

    def spustVytvoreniSqlVrstvy(self, synchronne: bool) -> None:
        """
        Zajistí spuštění vytváření SQL vrstvy.

        Args:
            synchronne: Příznak, zda funkci 1 spustit synchronně nebo
                asynchronně.
        """

        def nastavUlohy(nazev_ulohy: str) -> List[Uloha[Any, Any, Any]]:
            """
            Pomocná funkce pro nastavení úloh pro zpracování.

            Args:
                nazev_ulohy: Název úlohy.

            Returns:
                List[Uloha[Any, Any, Any]]: Seznam úloh ke spuštění.
            """

            ulohy: List[Uloha[Any, Any, Any]] = []

            for i in range(1, 2):
                parametry: dict[str, Any] = {
                    "par_1": i,
                    "par_2": "",
                }
                uloha = Uloha(
                    nazev=nazev_ulohy,
                    funkce=vytvoreniSqlVrstvy,
                    parametry_vstup=parametry,
                    on_start=vytvoreniSqlVsrtvy_onStart,
                    on_zpracovani=vytvoreniSqlVsrtvy_onZpracovani,
                    on_konec=vytvoreniSqlVsrtvy_onKonec,
                )
                ulohy.append(uloha)

            return ulohy

        def vytvoreniSqlVrstvy(
            *,
            nazev_ulohy: str,
            par_1: int,
            par_2: str,
            on_zpracovani: OnZpracovaniCB[str] | None = None,
        ) -> str:
            sqlDotaz = (
                "select seg_id, tp_tudu, geometry GEOM "
                "from lino_test.pts_fake_uv_f where tp_tudu='1901NG'"
            )
            if self._okno.chbChybnySql.isChecked():
                sqlDotaz = "s" + sqlDotaz
            styl = self._okno.leQmlSoubor.text()
            umisteni_lokalni = self._okno.chbLokalniQml.isChecked()
            nazev_vrstvy = f"vrstva_test_{par_1}"
            skupina = self._okno.VstupSkupina_1.currentText()
            poradi = self._okno.sbPoradi.value()
            self._fwt.workflow.qgis.vytvorVrstvuSql(
                sqlDotaz,
                "GEOM",
                "SEG_ID",
                styl,
                umisteni_lokalni,
                nazev_vrstvy,
                skupina,
                poradi,
                TypGeometrie.LineString,
                5514,
                False,
            )
            return f"Byla vložena vrstva: {nazev_vrstvy}"

        # ----------------------------------------------------------------------

        def vytvoreniSqlVsrtvy_onStart(nazev_ulohy: str) -> None:
            """Callback pro start úlohy (OnStart)."""
            self._okno.Vystup_1.appendPlainText(f"[{nazev_ulohy}] start úlohy")

        # ----------------------------------------------------------------------

        def vytvoreniSqlVsrtvy_onZpracovani(
            nazev_ulohy: str, parametry: str
        ) -> None:
            """Callback pro průběh zpracování (OnZpracovaniCB)."""
            self._okno.Vystup_1.appendPlainText(f"[{nazev_ulohy}] {parametry}")

        # ----------------------------------------------------------------------

        def vytvoreniSqlVsrtvy_onKonec(
            nazev_ulohy: str,
            stav: StavUlohy,
            vysledek: Any,
            vyjimka: Exception | None,
        ) -> None:
            """Callback pro konec úlohy (OnKonec)."""
            if stav == StavUlohy.OK:
                self._okno.Vystup_1.appendPlainText(
                    f"[{nazev_ulohy}] úspěch, výsledek: {vysledek}"
                )
                self._fwt.integrace.qgis.messageBar_text(
                    TypHlaseni.SUCCESS,
                    f"[{nazev_ulohy}]",
                    f"úspěch, výsledek: {vysledek}",
                )
            else:
                self._okno.Vystup_1.appendPlainText(
                    f"[{nazev_ulohy}] chyba, výjimka: {vyjimka}"
                )
                self._fwt.integrace.qgis.messageBar_text(
                    TypHlaseni.CRITICAL,
                    f"[{nazev_ulohy}]",
                    f"chyba, výjimka: {vyjimka}",
                )

        # ----------------------------------------------------------------------

        try:
            if synchronne:
                ulohy = nastavUlohy("SQL vrstva - synchronně")
                self._fwt.synch.spustUlohy(ulohy)
            else:
                ulohy = nastavUlohy("SQL vrstva - asynchronně")
                self._fwt.asynch.spustUlohy(ulohy)
        except ChybaValidaceUlohy as e:
            self._okno.Vystup_1.appendPlainText(f"CHYBA validace úlohy: {e}")

    # ----------------------------------------------------------------------
