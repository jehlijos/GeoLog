from __future__ import annotations

from enum import Enum


class TypGeometrie(str, Enum):
    """Typ geometrie vykreslené ve vrstvě QGIS.

    Dědí ze str kvůli snadnému logování/serializaci.
    """

    Point = "Point"
    LineString = "LineString"
    Polygon = "Polygon"


# ----------------------------------------------------------------------
