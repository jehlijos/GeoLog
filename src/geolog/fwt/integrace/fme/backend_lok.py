from __future__ import annotations

import os
import subprocess
from typing import Optional, final

from ...kontext import KontextFWT
from ...uloha import OnZpracovaniCB
from .backend_base import FmePozadavekSpusteni, FmeSpusteniVysledek


@final
class FmeLokBackend:
    def __init__(self, kontext: KontextFWT):
        self._kontext = kontext

    # -----------------------------------------------------------------------------------------

    def spustWorkspace(
        self,
        *,
        pozadavek: FmePozadavekSpusteni,
        nazev_ulohy: str,
        on_zpracovani: Optional[OnZpracovaniCB[str]] = None,
        timeout_s: float = 90.0,
    ) -> FmeSpusteniVysledek:
        """
        Spustí FME workspace jako lokální proces a sleduje jeho výstup.

        Args:
            pozadavek: Požadavek spuštění FME workspace (cesta k .fmw a
                parametry).
            nazev_ulohy: Název úlohy pro logování.
            on_zpracovani: Callback pro zpracování řádků logu.
            timeout_s: Časový limit pro spuštění procesu (v sekundách).

        Returns:
            FmeSpusteniVysledek: (úspěch, zpráva, exit code)

        Raises:
            FmeLokBackendError: Pokud dojde k chybě při konfiguraci nebo
                spuštění FME procesu.
            FmeWorkspaceNotFoundError: Pokud nebyl nalezen workspace .fmw.
            FmeExecutableNotFoundError: Pokud nebyl nalezen FME.EXE.
        """

        class FmeLokBackendError(RuntimeError):
            """Základní výjimka pro chyby lokálního FME backendu.

            Tj. chyby konfigurace/spuštění (ne "FME translation failed").
            """

        class FmeWorkspaceNotFoundError(FmeLokBackendError):
            def __init__(self, workspace: str):
                super().__init__(f"Workspace .fmw nebyl nalezen:\n{workspace}")
                self.workspace = workspace

        class FmeExecutableNotFoundError(FmeLokBackendError):
            def __init__(self, exe_path: str):
                super().__init__(
                    "V kontextu není platná cesta k FME aplikaci."
                )
                self.exe_path = exe_path

        ws_path = pozadavek.workspace
        if not ws_path.endswith(".fmw"):
            ws_path += ".fmw"
        ws_path = os.path.normpath(ws_path)
        if not ws_path or not os.path.isfile(ws_path):
            raise FmeWorkspaceNotFoundError(ws_path)

        fme_exe = self._kontext.fme_aplikace
        if not fme_exe or not os.path.isfile(fme_exe):
            raise FmeExecutableNotFoundError(fme_exe or "")

        cmd: list[str] = [fme_exe, ws_path]
        for k, v in (pozadavek.parametry or {}).items():
            # Pro jistotu rozbalime promenne prostredi (%TEMP%, %USERPROFILE%)
            # a kratky zapis domovske slozky (~), pokud se v parametru objevi.
            # ID:
            # hodnota_parametru = v
            # if "%" in hodnota_parametru or "~" in hodnota_parametru:
            #     hodnota_parametru = os.path.expandvars(
            #         os.path.expanduser(hodnota_parametru)
            #     )
            # cmd.extend([f"--{k}", hodnota_parametru])
            cmd.extend([f"--{k}", v])

        # FME procesu predame jednotny TEMP/TMP adresar z kontextu pluginu.
        # Tim omezime zavislost na nastaveni konkretniho PC.
        #
        # env = os.environ.copy()
        # temp_adresar = os.path.normpath(self._kontext.temp_adresar)
        # if temp_adresar:
        #     env["TEMP"] = temp_adresar
        #     env["TMP"] = temp_adresar

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                # env=env,
            )
        except Exception as e:
            raise FmeLokBackendError(f"Chyba při startu FME: {e}") from e

        lines: list[str] = []

        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                ln = line.rstrip("\r\n")
                lines.append(ln)
                if on_zpracovani:
                    try:
                        on_zpracovani(nazev_ulohy, ln)
                    except Exception:
                        pass
        finally:
            try:
                if proc.stdout:
                    proc.stdout.close()
            except Exception:
                pass

        try:
            exit_code = proc.wait(
                timeout=timeout_s if timeout_s and timeout_s > 0 else None
            )
        except subprocess.TimeoutExpired:
            exit_code = 1

        ok = exit_code == 0
        raw_log = "\n".join(lines).strip()
        msg = "OK" if ok else "FME skončilo chybou."
        if raw_log:
            msg += f"\n\n--- FME translation log ---\n{raw_log}"
        return ok, msg, exit_code

    # -----------------------------------------------------------------------------------------
