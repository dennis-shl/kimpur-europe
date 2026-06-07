# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)
MODULE_NAME = "effective_date_change"


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env["ir.module.module"].search([("name", "=", MODULE_NAME)], limit=1)
    if not module:
        _logger.info("Legacy module %s is not present; nothing to uninstall.", MODULE_NAME)
        return

    if module.state not in ("installed", "to upgrade"):
        _logger.info(
            "Legacy module %s is in state %s; uninstall scheduling skipped.",
            MODULE_NAME,
            module.state,
        )
        return

    _logger.info("Scheduling legacy module %s for uninstall during migration.", MODULE_NAME)
    module.button_uninstall()
