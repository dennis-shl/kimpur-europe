from collections import defaultdict

from markupsafe import Markup, escape

from odoo import api, models
from odoo.tools import plaintext2html, get_lang, float_round


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

    def get_consignor_adrress_without_country(self, partner_id):
        address_format = partner_id._get_address_format()
        args = defaultdict(str, {
            'country_code': partner_id.country_id.code or '',
            'country_name': '',
            'company_name': '',
        })
        for field in partner_id._formatting_address_fields():
            args[field] = partner_id[field] or ''

        return address_format % args

    def get_consignor_country(self, partner_id):
        if not partner_id or not partner_id.country_id:
            return ""

        return partner_id.country_id.display_name

    def _get_intrastat_code(self, product):
        if 'intrastat_code_id' not in product._fields:
            return ''
        return product.intrastat_code_id.code or ''

    def _get_packaging_quantity(self, move):
        if 'packaging_uom_qty' in move._fields:
            return move.packaging_uom_qty
        if 'product_packaging_quantity' in move._fields:
            return move.product_packaging_quantity
        return move.quantity

    def _get_packaging_name(self, move):
        if 'packaging_uom_id' in move._fields:
            return move.packaging_uom_id.display_name or ''
        if 'product_packaging_id' in move._fields:
            return move.product_packaging_id.display_name or ''
        return ''

    def _get_product_name_html(self, product):
        name = Markup('<strong>%s</strong><br/>') % (product.name or '')
        hs_code = product.hs_code
        if hs_code:
            name += Markup('HS: %s<br/>') % hs_code
        return name + Markup('<br/>')

    def get_consignee_name_address(self, picking):
        partner = picking.partner_id

        if not partner:
            return ""

        address = plaintext2html(partner.contact_address or '')
        contact_fields = []
        if not partner.is_company and partner.display_name:
            contact_fields.append(partner.display_name)
        if partner.phone:
            contact_fields.append(partner.phone)
        return Markup('%s%s') % (", ".join(contact_fields), address)

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
            info = Markup('<strong>%s</strong><br/>') % name
            address = partner.with_context({'show_address': True, 'address_inline': True}).display_name
            excess = address.find(',') + 1
            address = address[excess::]
            info += escape(address)
            info += Markup('<br/><br/>')
        else:
            info = picking.sale_id.partner_shipping_id.with_context({'show_address': True}).display_name if picking.sale_id else ''
            if info:
                info = plaintext2html(info)
            else:
                info = Markup('<br/>')

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
        info = picking.successive_carrier_address
        forwarder = picking.carrier_partner
        note = picking.carrier_notes
        note = plaintext2html(note or '')

        return {
            'info': plaintext2html(info._display_address() if info else ''),
            'forwarder': plaintext2html(forwarder._display_address() if forwarder else ''),
            'note': note,
            'carrier_details': plaintext2html(picking.carrier_details or '')
        }

    def get_sum_data(self, o):
        lines = o.move_ids
        volume_sum = 0
        weigth_sum = 0

        for line in lines:
            volume_sum += line.quantity * line.product_id.volume
            weigth_sum += line.quantity * line.product_id.weight

        return {
            'weigth_sum': float_round(weigth_sum, precision_digits=2, rounding_method='HALF-UP'),
            'volume_sum': float_round(volume_sum, precision_digits=2, rounding_method='HALF-UP'),
        }

    def get_lines(self, o):
        lines = o.move_ids
        product_lines = []

        for item in lines:
            product_lines.append({
                'name': self._get_product_name_html(item.product_id),
                'number': self._get_packaging_quantity(item),
                'weight': item.quantity * item.product_id.weight,
                'volume': item.quantity * item.product_id.volume,
                'method_packing': self._get_packaging_name(item),
                'intrastat_code': self._get_intrastat_code(item.product_id)
            })

        return product_lines

    def get_product_data(self, line):
        number = self._get_packaging_quantity(line.move_id)
        weight = line.product_id.weight * number
        volume = line.quantity

        return {
            'name': self._get_product_name_html(line.product_id),
            'number': number,
            'weight': ' ' if weight == 0 else weight,
            'volume': ' ' if volume == 0 else volume,
            'method_packing': self._get_packaging_name(line.move_id),
            'intrastat_code': self._get_intrastat_code(line.product_id)
        }

    def get_goods_data(self, picking):
        date_format = get_lang(self.env).date_format
        return {
            'place': self.get_consignor_adrress_without_country(picking.place_contact) if picking.place_contact else self.get_consignor_adrress_without_country(picking.sudo().company_id.partner_id),
            'state': self.get_consignor_country(picking.place_contact) if picking.place_contact else self.get_consignor_country(picking.sudo().company_id.partner_id),
            'date': (picking.date or picking.scheduled_date).strftime(date_format) if picking.date or picking.scheduled_date else ''
        }

    def get_incoterm(self, picking):
        if not picking.sale_id or not picking.sale_id.incoterm:
            return ''
        return picking.sale_id.incoterm.code or ''

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
            'get_annexed_documents': self.get_annexed_documents,
            'get_notes': self.get_notes,
            'get_car_data': self.get_car_data,
            'get_carrier_data': self.get_carrier_data,
            'get_product_data': self.get_product_data,
            'get_sum_data': self.get_sum_data,
            'get_lines': self.get_lines,
            'get_goods_data': self.get_goods_data,
            'get_incoterm': self.get_incoterm,
        }
