# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_packing_list_send(self):
        self.ensure_one()
        ctx = dict(self.env.context or {})

        template_id = self.env.ref(
            "packing_list_by_mail.email_template_edi_packing_list",
            raise_if_not_found=False,
        )
        compose_form_id = self.env.ref(
            "mail.email_compose_message_wizard_form", raise_if_not_found=False
        )

        ctx.update(
            {
                "model_description": _("Packing List"),
                "default_model": "stock.picking",
                "active_model": "stock.picking",
                "active_id": self.picking_ids.ids[0],
                "default_res_id": self.picking_ids.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id.id,
                "default_composition_mode": "comment",
                "custom_layout": "packing_list_by_mail.mail_notification_packing_list",
                "force_email": True,
                "mail_notify_author": True,
            }
        )

        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id.id, "form")],
            "view_id": compose_form_id.id,
            "target": "new",
            "context": ctx,
        }
