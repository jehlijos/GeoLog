from typing import TypeVar

T = TypeVar("T")


def notNone(hodnota: T | None, *, zprava: str | None = None) -> T:
    """
    Vrátí `hodnota` a zúží typ z `T | None` na `T` (assert varianta).
    Pozn.: `assert` lze vypnout při spuštění Pythonu s `-O`.

        Args:
            hodnota: Hodnota, která má být zkontrolována.
            zprava: Volitelná zpráva pro případ selhání kontroly.

        Returns:
            T: Původní hodnota `hodnota`, zúžená na typ `T`.
    """
    assert hodnota is not None, (
        zprava or "not_none(): očekávána non-None hodnota"
    )
    return hodnota


# ----------------------------------------------------------------------


def requireNotNone(hodnota: T | None, *, zprava: str | None = None) -> T:
    """
    Vrátí `hodnota` a zúží typ z `T | None` na `T` (výjimka, kontrola vždy).

        Args:
            hodnota: Hodnota, která má být zkontrolována.
            zprava: Volitelná zpráva pro případ selhání kontroly.

        Returns:
            T: Původní hodnota `hodnota`, zúžená na typ `T`.
    """
    if hodnota is None:
        raise ValueError(
            zprava or "require_not_none(): hodnota nesmí být None"
        )
    return hodnota


# ----------------------------------------------------------------------
