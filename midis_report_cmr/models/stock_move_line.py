# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import frozendict


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'