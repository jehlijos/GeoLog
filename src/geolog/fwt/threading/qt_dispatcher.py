from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PyQt5.QtCore import QObject, QThread, pyqtSignal


@dataclass(frozen=True)
class _GuiCall:
    funkce: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class QtDispatcher(QObject):
    """
    Pomůcka pro bezpečné vyvolání callbacku v GUI threadu.
    Implementace je postavená na Qt signálu.
    """

    _sig_call = pyqtSignal(object)

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._sig_call.connect(self._onCall)

    # ----------------------------------------------------------------------

    def zavolejVGui(
        self,
        funkce: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Zavolá funkci v GUI threadu s danými argumenty.

        Args:
            funkce: Funkce, která má být zavolána
                v GUI threadu.
            *args: Pozice argumentů pro funkci.
            **kwargs: Klíčové argumenty pro funkci.
        """
        call = _GuiCall(funkce=funkce, args=args, kwargs=kwargs)

        # Pokud už běžíme v GUI threadu (tj. ve threadu tohoto QObjectu),
        # zavoláme rovnou.
        if QThread.currentThread() == self.thread():
            self._onCall(call)
            return

        # Jinak pošleme do GUI threadu přes queued signal.
        self._sig_call.emit(call)

    # ----------------------------------------------------------------------

    def _onCall(self, call_obj: object) -> None:
        """
        Zpracuje volání callbacku v GUI threadu.

        Args:
            call_obj (object): Objekt s informacemi o volání.
        """
        call = call_obj  # runtime typový cast
        try:
            assert isinstance(call, _GuiCall)
            call.funkce(*call.args, **call.kwargs)
        except Exception:
            import traceback

            traceback.print_exc()

    # ----------------------------------------------------------------------
