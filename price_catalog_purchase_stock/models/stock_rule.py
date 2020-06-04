# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRule(models.Model):
    """Override PurchaseOrder for catalog prices."""

    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        partner_id = res.get("partner_id", None)
        if partner_id is not None:
            partner = self.env["res.partner"].browse(partner_id)
            if partner.purchase_catalog_id:
                res["price_catalog_id"] = partner.purchase_catalog_id.id
        return res

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        partner = po.partner_id
        if partner.purchase_catalog_id:
            price_catalog = partner.purchase_catalog_id

            taxes = product_id.supplier_taxes_id
            fpos = po.fiscal_position_id
            taxes_id = fpos.map_tax(taxes, product_id, partner) if fpos else taxes
            if taxes_id:
                taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

            seller_price = price_catalog.get_price(product_id, po.date_order)
            price_unit = (
                self.env["account.tax"]._fix_tax_included_price_company(
                    seller_price, product_id.supplier_taxes_id, taxes_id, company_id
                )
                if seller_price
                else 0.0
            )
            if (
                price_unit
                and price_catalog
                and po.currency_id
                and price_catalog.currency_id != po.currency_id
            ):
                price_unit = price_catalog.currency_id._convert(
                    price_unit,
                    po.currency_id,
                    po.company_id,
                    po.date_order or fields.Date.today(),
                )

            res.update({"price_unit": price_unit})
        return res
