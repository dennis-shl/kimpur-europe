from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    name = fields.Char('Reference', default='/', copy=False, index=True, readonly=False)
    annexed_documents = fields.Char()

    id_number_25 = fields.Char('Ident. Number 25')
    car_25 = fields.Char()
    sidecar_25 = fields.Char()
    type_26 = fields.Char()
    car_26 = fields.Char()
    sidecar_26 = fields.Char()

    carrier_partner = fields.Many2one('res.partner', string='Carrier/Forwarder')
    successive_carrier_address = fields.Many2one('res.partner', string='Successive Carriers')
    carrier_notes = fields.Text(string='Carrier`s Reservations and Observations')
    carrier_details = fields.Text(string='Signature and stamp of the carrier 23')

    place = fields.Char()
    place_contact = fields.Many2one('res.partner', string='Place')
    cmr_country = fields.Char('Country')
    date = fields.Date()

    is_delivery_manual = fields.Boolean('Select Partner', default=False)
    delivery_address_id = fields.Many2one('res.partner')

    sender_instructions = fields.Char("Sender's Instructions")
