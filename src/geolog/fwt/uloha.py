from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from typing_extensions import ParamSpec
import uuid

from .stav import StavUlohy

P = ParamSpec("P")
R = TypeVar("R")
TProgress = TypeVar("TProgress")

OnStart = Optional[Callable[[str], None]]

# callback pro progress: (nazev_ulohy, parametry)
OnZpracovaniCB = Callable[[str, TProgress], None]
OnZpracovani = Optional[OnZpracovaniCB[TProgress]]

# on_konec: (nazev_ulohy, stav, vysledek, vyjimka)
OnKonec = Optional[
    Callable[[str, StavUlohy, Optional[R], Optional[Exception]], None]
]


@dataclass
class Uloha(Generic[P, R, TProgress]):
    nazev: str

    # funkce přijímá "nějaké parametry" P a vrací R
    # (type-checker pak umí hlídat shodu v místě vytváření konkrétní Uloha)
    funkce: Callable[P, R]

    parametry_vstup: Dict[str, Any] = field(default_factory=lambda: {})

    on_start: OnStart = None
    on_zpracovani: OnZpracovani[TProgress] = None
    on_konec: OnKonec[R] = None

    id_ulohy: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=lambda: {})

    vysledek: Optional[R] = None
    vyjimka: Optional[Exception] = None
    stav: Optional[StavUlohy] = None
