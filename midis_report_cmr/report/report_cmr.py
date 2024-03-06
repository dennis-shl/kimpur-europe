from odoo import api, models
from odoo.tools import plaintext2html, get_lang


class ReportCMR(models.AbstractModel):
    _name = 'report.midis_report_cmr.report_cmr'
    _description = 'CMR Report'

    def get_consignor_name(self, picking):
        company_name = picking.sudo().company_id.partner_id.commercial_company_name
        # address = partner.with_context({'show_address': True, 'address_inline': True}).display_name or ''
        # address = partner.contact_address or ''
        # address = partner.display_name or ''
        # address = plaintext2html(address)
        # o.commercial_company_name
        # o._display_address(without_company=True)
        return company_name

    def get_consignor_address(self, picking):
        return picking.sudo().company_id.partner_id._display_address(without_company=True)


    def get_consignee_name_address(self, picking):
        partner = picking.sale_id.partner_id
        address = partner.contact_address or ''
        address = plaintext2html(address)
        return address

    def get_partner_delivery_address_next(self, picking):
        if picking.is_delivery_manual and picking.delivery_address_id:
            delivery_partner = picking.delivery_address_id
            name = delivery_partner.name
            partner = delivery_partner
            if partner.parent_id:
                delivery_partner = partner
                name = partner.parent_id.name
            if not partner.parent_id:
                delivery_partner = self.env['res.partner'].search([('parent_id', '=', partner.id)], limit=1)
            if delivery_partner:
                partner = delivery_partner
            info = '<strong>' + name + '</strong><br/>'
            address = partner.with_context({'show_address': True, 'address_inline': True}).display_name
            excess = address.find(',') + 1
            address = address[excess::]
            info = info + address
            info = info + '<br/><br/>'
        else:
            info = picking.sale_id.partner_shipping_id.with_context({'show_address': True}).display_name if picking.sale_id else ''
            if info:
                info = info.replace('\n', '<br/>')
            else:
                info = '<br/>'

        return info

    def get_partner_picking_address(self, o):
        info = {
            'place': '',
            'state': '',
            'date': ''
        }
        pick_up = self.env['res.partner'].search([('parent_id', '=', self.env.company.partner_id.id), ('type', '=', 'other')])
        info['place'] = pick_up.city
        info['state'] = pick_up._get_country_name()

        return info

    def get_annexed_documents(self, picking):
        return picking.annexed_documents

    def get_notes(self, picking):
        return picking.note

    def get_car_data(self, picking):
        return {
            'id_number_25': picking.id_number_25,
            'car_25': picking.car_25,
            'sidecar_25': picking.sidecar_25,
            'type_26': picking.type_26,
            'car_26': picking.car_26,
            'sidecar_26': picking.sidecar_26,
        }

    def get_carrier_data(self, picking):
        info = picking.carrier_address
        if info:
            info = info.replace('\n', '<br/>')
        else:
            info = '<br/>'
        note = picking.carrier_notes
        if note:
            note = note.replace('\n', '<br/>')
        else:
            note = '<br/>'

        info = info + '<br/><br/>'
        return {
            'info': info,
            'note': note,
            'carrier_details': plaintext2html(picking.carrier_details)
        }

    def get_product_data(self, line):
        name = line.product_id.name
        name = '<strong>' + name + '</strong><br/>'
        hs_code = line.product_id.hs_code

        if hs_code:
            name = name + 'HS: ' + hs_code + '<br/>'

        name = name + '<br/>'

        number = line.quantity
        weight = line.product_id.weight * number
        volume = line.product_id.volume * number

        return {
            'name': name,
            'number': number,
            'weight': ' ' if weight == 0 else weight,
            'volume': ' ' if volume == 0 else volume,
            'method_packing': line.move_id.product_packaging_id.display_name or ''
        }

    def get_goods_data(self, picking):
        date_format = get_lang(self.env).date_format
        return {
            'place': picking.place or self.get_consignor_name(picking),
            'state': picking.cmr_country or self.get_consignor_address(picking),
            'date': picking.date and picking.date.strftime(date_format) or picking.scheduled_date.strftime(date_format)
        }

    def get_incoterm(self, picking):
        incoterm = ''
        if picking.sale_id:
            incoterm_id = picking.sale_id.incoterm
            incoterm = incoterm_id.code
        return incoterm

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('midis_report_cmr.report_cmr')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'report_type': data.get('report_type') if data else '',
            'get_consignor_name': self.get_consignor_name,
            'get_consignor_address': self.get_consignor_address,
            'get_consignee_name_address': self.get_consignee_name_address,
            'get_partner_delivery_address_next': self.get_partner_delivery_address_next,
            # 'get_partner_picking_address': self.get_partner_picking_address,
            'get_annexed_documents': self.get_annexed_documents,
            'get_notes': self.get_notes,
            'get_car_data': self.get_car_data,
            'get_carrier_data': self.get_carrier_data,
            'get_product_data': self.get_product_data,
            'get_goods_data': self.get_goods_data,
            'get_incoterm': self.get_incoterm,
        }