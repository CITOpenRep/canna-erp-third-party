# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def execute(self):
        """
        Relaunch the account chart setup wizard for multi-company setups
        """
        ctx = self.env.context.copy()
        if self.chart_template_id and self.chart_template_id.l10n_be_coa_multilang:
            module = "l10n_be_coa_multilang"
            todo = "l10n_be_coa_multilang_config_action_todo"
            todo = self.env.ref("{}.{}".format(module, todo))
            if todo.state == "done":
                todo.state = "open"
            ctx.update({"default_charts": "l10n_be_coa_multilang"})
        # The default_get of the standard accounting setup wizard assumes that
        # the user's default company is equal to the company selected in the
        # settings but doesn't check which may give wrong results.
        # We therefor have added this check here.
        # TODO: make PR on https://github.com/odoo/odoo
        if self.company_id != self.env.user.company_id:
            raise UserError(
                _("Your 'Current Company' must be set to '%s' !") % self.company_id.name
            )
        return super(ResConfigSettings, self.with_context(ctx)).execute()
