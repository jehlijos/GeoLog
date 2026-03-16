from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar, cast

from ..threading.qt_dispatcher import QtDispatcher

T = TypeVar("T", bound=Callable[..., Any])


class CallbackWrapper:

    def __init__(self, dispatcher: QtDispatcher):
        self._dispatcher: QtDispatcher = dispatcher

    # ----------------------------------------------------------------------

    def wrap(self, callback: Optional[T]) -> Optional[T]:
        """
        Zabalí callback tak, aby byl vždy volán v GUI threadu.

        Args:
            callback (Optional[T]): Callback, který má být zabalen.
        """
        if callback is None:
            return None

        @functools.wraps(callback)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Callbacky směrujeme do GUI threadu přes QtDispatcher
            # (queued signal).
            # Návratová hodnota se nepřenáší (zavolání je asynchronní
            # vůči worker threadu).
            return self._dispatcher.zavolejVGui(callback, *args, **kwargs)

        return cast(T, wrapped)

    # ----------------------------------------------------------------------
