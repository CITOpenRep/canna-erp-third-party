# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model_create_multi
    def create(self, vals_list):
        daf_models = safe_eval(
            self.env["ir.config_parameter"].sudo().get_param(
                "mail_thread_disable_auto_followers"
            )
            or "[]"
        )
        if self._name in daf_models:
            ctx = dict(
                self.env.context,
                mail_create_nosubscribe=True,
                mail_thread_disable_auto_followers=daf_models,
            )
            self = self.with_context(ctx)
        return super().create(vals_list)

    def write(self, vals):
        daf_models = safe_eval(
            self.env["ir.config_parameter"].sudo().get_param(
                "mail_thread_disable_auto_followers"
            )
            or "[]"
        )
        if self._name in daf_models:
            ctx = dict(self.env.context, mail_thread_disable_auto_followers=daf_models)
            self = self.with_context(ctx)
        return super().write(vals)

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, **kwargs):
        """
        We also need to handle the case where the create/write context
        is gone (e.g. mail wizard).
        """
        if self.env.context.get("mail_post_autofollow"):
            daf_models = safe_eval(
                self.env["ir.config_parameter"].sudo().get_param(
                    "mail_thread_disable_auto_followers"
                )
                or "[]"
            )
            if self._name in daf_models:
                ctx = self.env.context.copy()
                del ctx["mail_post_autofollow"]
                ctx["mail_create_nosubscribe"] = True
                self = self.with_context(ctx)
        return super().message_post(*args, **kwargs)

    def message_subscribe(self, *args, **kwargs):
        """
        In some cases the message_subscribe is called before the write
        (e.g. sale order confirmation).
        """
        if "mail_thread_disable_auto_followers" not in self.env.context:
            daf_models = safe_eval(
                self.env["ir.config_parameter"].sudo().get_param(
                    "mail_thread_disable_auto_followers"
                )
                or "[]"
            )
            if self._name in daf_models:
                # the Odoo standard addons use a mix of args and kwargs to call
                # this method hence we need messy code to copy with this
                args_new = []
                if args:
                    args_new.append(None)
                    for arg in args[1:]:
                        args_new.append(arg)
                args = tuple(args_new)
            if "partner_ids" in kwargs:
                kwargs["partner_ids"] = None
        return super().message_subscribe(*args, **kwargs)

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        daf_models = self.env.context.get("mail_thread_disable_auto_followers", [])
        if self._name in daf_models:
            return []
        return super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
