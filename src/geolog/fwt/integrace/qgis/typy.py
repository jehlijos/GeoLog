from __future__ import annotations

from enum import Enum


class TypHlaseni(str, Enum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
