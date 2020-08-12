# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.partner_invoice_id = (
                self.partner_shipping_id
            ) = self.payment_term_id = self.fiscal_position_id = False

        partner_user = (
            self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        )
        values = {
            "pricelist_id": self.partner_id.property_product_pricelist
            and self.partner_id.property_product_pricelist.id
            or False,
            "payment_term_id": self.partner_id.property_payment_term_id
            and self.partner_id.property_payment_term_id.id
            or False,
        }
        user_id = partner_user.id or self.env.uid
        if self.user_id.id != user_id:
            values["user_id"] = user_id

        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.use_invoice_terms")
            and self.env.company.invoice_terms
        ):
            values["note"] = self.with_context(
                lang=self.partner_id.lang
            ).env.company.invoice_terms

        # Use team of salesman if any otherwise leave as-is
        values["team_id"] = (
            partner_user.team_id.id
            if partner_user and partner_user.team_id
            else self.team_id
        )
        self.update(values)
        partner_action_obj = self.env["crm.partner.action"]
        values["user_id"] = self._uid
        if "pricelist_id" in values and values["pricelist_id"]:
            if isinstance(values["pricelist_id"], int):
                values["pricelist_id"] = int(values["pricelist_id"])

        cpart = self.partner_id.commercial_partner_id
        partner_ids = [cpart.id] + [x.id for x in cpart.child_ids]
        dom = [("partner_id", "in", partner_ids), ("state", "=", "open")]
        action_ids = partner_action_obj.search(dom)
        message_body = ""
        for action in partner_action_obj.search([("partner_id", "in", action_ids.ids)]):
            if not action.user_id.id or self._uid == action.user_id.id:
                message_body += action.description
                if action.comments:
                    message_body += "\n\n" + action.comments
                message_body += "\n\n"
        if message_body:
            values["warning"] = {
                "title": _("Open Actions"),
                "message": _(
                    "There are still open actions for this partner. "
                    "Please check if there are any relevant actions"
                )
                + "\n\n"
                + message_body,
            }
