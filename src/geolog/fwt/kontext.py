from qgis.gui import QgisInterface
from dataclasses import dataclass
from pathlib import Path
import tempfile
import win32api

# doplněno
import re
from typing import Optional


@dataclass(frozen=True, slots=True)
class DbKonfigurace:
    db_engine: str
    host: str
    port: int
    databaze: str
    jmeno: str
    heslo: str


@dataclass(frozen=True, slots=True)
class MultiAdresare:
    lokalni: Path
    sdileny: Path


class KontextFWT:
    """
    Sdílený kontext po celý život pluginu.
    """

    def __init__(
        self,
        iface: QgisInterface,
        plugin_root: Path,
        db_konfigurace: DbKonfigurace,
        qml_adresar: MultiAdresare,
        fme_adresar: MultiAdresare,
    ):
        self.iface = iface

        # Konfigurace pro integrace
        self.db_konfigurace = db_konfigurace
        self.qml_adresar = MultiAdresare(
            plugin_root.joinpath(qml_adresar.lokalni), qml_adresar.sdileny
        )
        self.fme_adresar = MultiAdresare(
            plugin_root.joinpath(fme_adresar.lokalni), fme_adresar.sdileny
        )

        self.uzivatel_ad = win32api.GetUserNameEx(2)

        # Dočasný adresář uživatele
        self.temp_adresar = tempfile.gettempdir()
        # Cesta k rootu pluginu
        self.plugin_root = plugin_root

        # Cesta k aplikaci FME
        self.fme_aplikace = self._urciCestuFME()

    # ----------------------------------------------------------------------

    def _urciCestuFME(self) -> str:
        """Určí cestu k aplikaci FME (pouze fme.exe, nikdy GUI Workbench).

        Returns:
            str: Vrací cestu k existujícímu fme.exe, nebo prázdný řetězec.
        """

        # Zkusíme standardní cestu (engine)
        standardni_cesta_engine = "C:\\Program Files\\FME\\fme.exe"
        if Path(standardni_cesta_engine).exists():
            return standardni_cesta_engine

        # Pokud není FME na standardní cestě,
        # zkusíme zjistit jeho umístění z registrů Windows
        import winreg

        def _ctiHodnotuZRegistru(koren: int, vetev: str) -> Optional[str]:
            """
            Z registru načte hodnotu (typicky řetězec) z dané větve.

            Args:
                koren: Kořenová větev (např. winreg.HKEY_CLASSES_ROOT).
                vetev: Podvětev, ze které se má hodnota číst.

            Returns:
                Optional[str]: Vrací přečtenou hodnotu nebo None, pokud se
                    nepodařilo přečíst.
            """
            try:
                with winreg.OpenKey(koren, vetev) as k:
                    hodnota, _ = winreg.QueryValueEx(k, "")
                    if isinstance(hodnota, str) and hodnota.strip():
                        return hodnota.strip()
            except FileNotFoundError:
                return None
            except OSError:
                return None
            return None

        def _ctiPodvetveZRegistru(koren: int, cesta_shell: str) -> list[str]:
            """Vrátí cesty k `...\\command` pod větví `shell`.

            Typicky:
              - shell\\open\\command
              - shell\\FME_Workbench\\command

            Args:
                koren: Kořenová větev (např. winreg.HKEY_CLASSES_ROOT).
                cesta_shell: Cesta k větvi `shell` (např.
                    "FME.Workbench\\shell").

            Returns:
                list[str]: Vrací seznam cest k `...\\command` pod větví
                    `shell`.
            """
            seznam: list[str] = []
            # Preferuje standartní `open`
            seznam.append(cesta_shell + "\\open\\command")

            try:
                with winreg.OpenKey(koren, cesta_shell) as klic_shell:
                    i = 0
                    while True:
                        try:
                            podvetev = winreg.EnumKey(klic_shell, i)
                        except OSError:
                            break
                        i += 1
                        # přeskočí `open` (už je vložená jako první)
                        if podvetev.lower() == "open":
                            continue
                        seznam.append(
                            cesta_shell + "\\" + podvetev + "\\command"
                        )
            except FileNotFoundError:
                return seznam
            except OSError:
                return seznam

            return seznam

        def _urciCestuZPrikazu(prikaz: str) -> Optional[str]:
            """
            Z řetězce typu '"C:\\...\\app.exe" "%1"' vrátí cestu k exe.

            Args:
                prikaz: Řetězec s příkazem, který může obsahovat cestu k exe.

            Returns:
                Optional[str]: Vrací cestu k exe, pokud se podaří ji z příkazu
                    určit, nebo None, pokud se to nepodaří.
            """
            cmd = prikaz.strip()
            if not cmd:
                return None

            if cmd.startswith('"'):
                m = re.match(r'^"([^"]+?\.exe)"', cmd, flags=re.IGNORECASE)
                if m:
                    return m.group(1)

            m = re.match(r"^([^\s]+?\.exe)\b", cmd, flags=re.IGNORECASE)
            if m:
                return m.group(1)

            return None

        koren = winreg.HKEY_CLASSES_ROOT
        # určíme ProgID pro .fmw
        prog_id = _ctiHodnotuZRegistru(koren, ".fmw")
        if prog_id:
            # z ProgID vyhodnotíme aplikaci
            cesta_shell = f"{prog_id}\\shell"
            for podvetev in _ctiPodvetveZRegistru(koren, cesta_shell):
                prikaz = _ctiHodnotuZRegistru(koren, podvetev)
                if not prikaz:
                    continue
                cesta_exe = _urciCestuZPrikazu(prikaz)
                if cesta_exe and cesta_exe.lower().endswith(
                    "fmeworkbench.exe"
                ):
                    cesta_exe = str(Path(cesta_exe).parent) + "\\fme.exe"
                    if cesta_exe and Path(cesta_exe).exists():
                        # Akceptujeme pouze fme.exe (engine)
                        return cesta_exe

        raise RuntimeError(
            "Nelze určit cestu k FME engine (fme.exe). "
            "Zkontrolujte, že máte nainstalované FME a že .fmw soubory jsou "
            "spojeny s FME engine (fme.exe)."
        )

    # ----------------------------------------------------------------------
