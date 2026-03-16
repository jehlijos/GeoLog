from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import yaml
from qgis.gui import QgisInterface

from .integrace.integrace import Integrace
from .workflow.workflow_root import Workflow
from .kontext import KontextFWT, DbKonfigurace, MultiAdresare
from .typ_spousteni import IFwtSpoustec
from .spousteni import SynchronniSpoustec
from .spousteni.asynchronni import AsynchronniSpoustec
from .threading.qt_dispatcher import QtDispatcher
from .threading.callback_wrapper import CallbackWrapper


class FWT:

    def __init__(
        self, iface: QgisInterface, plugin_root: Path, max_pocet_vlaken: int
    ):
        main_window = iface.mainWindow()
        if main_window is None:
            raise RuntimeError("QgisInterface.mainWindow() vrátil None")

        dispatcher: QtDispatcher = QtDispatcher(main_window)
        wrapper: CallbackWrapper = CallbackWrapper(dispatcher)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=max_pocet_vlaken
        )

        oracle_konfigurace, qml_adresare, fme_adresare = (
            self._nacti_syspaths_konfiguraci(plugin_root)
        )
        self.kontext: KontextFWT = KontextFWT(
            iface, plugin_root, oracle_konfigurace, qml_adresare, fme_adresare
        )

        self.synch: IFwtSpoustec = SynchronniSpoustec()
        self.asynch: IFwtSpoustec = AsynchronniSpoustec(executor, wrapper)
        self.integrace: Integrace = Integrace(self.kontext)
        self.workflow: Workflow = Workflow(self)

    # ----------------------------------------------------------------------

    @staticmethod
    def _nacti_syspaths_konfiguraci(
        plugin_root: Path,
    ) -> tuple[DbKonfigurace, MultiAdresare, MultiAdresare]:
        config_path = plugin_root.joinpath("config", "syspaths_config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(
                f"Konfigurační soubor nebyl nalezen: {config_path}"
            )

        # Nacitani konfigurace ze syspaths_config.yaml
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        databaze = data.get("Databaze") or {}
        qml_cfg = data.get("QML_adresare") or {}
        fme_cfg = data.get("FME_adresare") or {}

        try:
            db = DbKonfigurace(
                db_engine=str(databaze["db_engine"]),
                host=str(databaze["host"]),
                port=int(databaze["port"]),
                databaze=str(databaze["databaze"]),
                jmeno=str(databaze["jmeno"]),
                heslo=str(databaze["heslo"]),
            )
            qml = MultiAdresare(
                lokalni=Path(str(qml_cfg["lokalni_adresar"])),
                sdileny=Path(str(qml_cfg["sdilena_slozka"])),
            )
            fme = MultiAdresare(
                lokalni=Path(str(fme_cfg["lokalni_adresar"])),
                sdileny=Path(str(fme_cfg["sdilena_slozka"])),
            )
        except KeyError as e:
            raise ValueError(
                f"Chybí povinný klíč v {config_path}: {e}"
            ) from e

        return db, qml, fme