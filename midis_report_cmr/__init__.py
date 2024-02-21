from . import models
from . import report
from odoo import api, SUPERUSER_ID


def initial_actions(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

