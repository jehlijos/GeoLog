from __future__ import annotations

from typing import TYPE_CHECKING

from .qgis.workflow_qgis import WorkflowQgis
from .fme.workflow_fme import WorkflowFme

if TYPE_CHECKING:
    from ..fwt import FWT


class Workflow:
    """Kořenový objekt pro orchestrace (workflow) nad FWT."""

    def __init__(self, fwt: FWT):
        # self._fwt = fwt
        self.qgis = WorkflowQgis(fwt)
        self.fme = WorkflowFme(fwt)
