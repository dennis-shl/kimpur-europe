from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hs_code = fields.Char('HS Code')


