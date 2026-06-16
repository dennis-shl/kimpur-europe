# -*- coding: utf-8 -*-
##############################################################################
#
#    Part of myACC. Proprietary and Confidential.
#    © 2026 myACC, IK. All rights reserved.
#
#    See LICENSE file for full copyright and licensing details.
#
#    This module is intended for internal use only and may not be
#    redistributed, copied, or modified without prior written permission
#    from myACC, IK.
#
##############################################################################

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_base_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Main UoM",
        compute="_compute_product_base_uom_id",
        readonly=True,
    )
    price_unit_base_uom = fields.Monetary(
        string="Unit Price (Main UoM)",
        compute="_compute_price_unit_base_uom",
        currency_field="currency_id",
        help="Unit price per the product main unit of measure from the sales pricelist.",
    )

    @api.depends("product_id", "product_id.uom_id", "display_type")
    def _compute_product_base_uom_id(self):
        for line in self:
            if line.display_type or not line.product_id:
                line.product_base_uom_id = False
            else:
                line.product_base_uom_id = line.product_id.uom_id

    def _get_pricelist_kwargs_base_uom(self):
        self.ensure_one()
        return {
            "quantity": self.product_uom_qty or 1.0,
            "uom": self.product_id.uom_id,
            "date": self._get_order_date(),
            "currency": self.currency_id,
        }

    def _get_pricelist_price_in_base_uom(self):
        """Return pricelist rule price for the product main UoM."""
        self.ensure_one()
        if not self.product_id or self.display_type or not self.product_uom_id:
            return 0.0
        if self.product_type == "combo":
            return 0.0

        product = self.product_id.with_context(**self._get_product_price_context())
        base_uom = product.uom_id
        product_taxes = product.taxes_id._filter_taxes_by_company(self.company_id)
        pricelist = self.order_id.pricelist_id
        kwargs = self._get_pricelist_kwargs_base_uom()

        if pricelist:
            rule_id = pricelist._get_product_rule(
                product=product,
                **kwargs,
            )
            if rule_id:
                price = self.env["product.pricelist.item"].browse(rule_id)._compute_price(
                    product=product,
                    **kwargs,
                )
            else:
                price = base_uom._compute_price(product.lst_price, base_uom)
        else:
            price = base_uom._compute_price(product.lst_price, base_uom)

        return product._get_tax_included_unit_price_from_price(
            price,
            product_taxes=product_taxes,
            fiscal_position=self.order_id.fiscal_position_id,
        )

    @api.depends(
        "product_id",
        "product_id.uom_id",
        "product_uom_id",
        "product_uom_qty",
        "product_no_variant_attribute_value_ids",
        "order_id.pricelist_id",
        "order_id.date_order",
        "order_id.fiscal_position_id",
        "currency_id",
        "company_id",
        "tax_ids",
        "display_type",
        "product_id.lst_price",
    )
    def _compute_price_unit_base_uom(self):
        for line in self:
            line.price_unit_base_uom = line._get_pricelist_price_in_base_uom()
