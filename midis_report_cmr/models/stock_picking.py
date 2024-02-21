from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    name = fields.Char('Reference', default='/', copy=False, index=True, readonly=False)
    annexed_documents = fields.Char()

    id_number_25 = fields.Char('Identification Number')
    car_25 = fields.Char('Car')
    sidecar_25 = fields.Char('Sidecar')
    type_26 = fields.Char('Type')
    car_26 = fields.Char('Car')
    sidecar_26 = fields.Char('Sidecar')

    carrier_address = fields.Text('Successive Carriers')
    carrier_notes = fields.Text(string='Carrier`s Reservations and Observations')

    place = fields.Char()
    country_id = fields.Many2one('res.country', default=lambda self: self.env['res.country'].search([('code', '=', 'LV')], limit=1))
    date = fields.Date()

    is_delivery_manual = fields.Boolean('Select Partner', default=False)
    delivery_address_id = fields.Many2one('res.partner')

    sender_instructions = fields.Char("Sender's Instructions")
