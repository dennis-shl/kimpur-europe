from odoo import api, models


class ReportCMR(models.AbstractModel):
    _name = 'report.midis_report_cmr.report_cmr'
    _description = 'CMR Report'

    def get_company_address(self):
        company = self.env.company.partner_id
        info = company.with_context({'show_address': True,'html_format': True, 'show_vat': True}).display_name

        return info + '<br/><br/>'

    def get_partner_delivery_address(self, o):
        partner = o.sale_id.partner_id if o.sale_id else False
        if partner:
            info = partner.with_context({'show_address': True, 'address_inline': True}).display_name
            excess = info.find(',') + 1
            info = info[excess::]
            info = info + '<br/><br/>'
            return info
        else:
            return ''

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
            address = partner.with_context({'show_address': True, 'address_inline': True})._get_name()
            excess = address.find(',') + 1
            address = address[excess::]
            info = info + address
            info = info + '<br/><br/>'
        else:
            info = picking.sale_id.partner_shipping_id.display_name if picking.sale_id else ''
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
            'volume': ' ' if volume == 0 else volume
        }

    def get_goods_data(self, picking):
        return {
            'place': picking.place,
            'state': picking.country_id.name,
            'date': picking.date
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
            'get_company_address': self.get_company_address,
            'get_partner_delivery_address': self.get_partner_delivery_address,
            'get_partner_delivery_address_next': self.get_partner_delivery_address_next,
            'get_partner_picking_address': self.get_partner_picking_address,
            'get_annexed_documents': self.get_annexed_documents,
            'get_notes': self.get_notes,
            'get_car_data': self.get_car_data,
            'get_carrier_data': self.get_carrier_data,
            'get_product_data': self.get_product_data,
            'get_goods_data': self.get_goods_data,
            'get_incoterm': self.get_incoterm,
        }