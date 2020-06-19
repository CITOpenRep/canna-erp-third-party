# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


def get_applicable_models(browselist):
    return list({m for rec in browselist for m in rec.get_applicable_models()})


def update_model_flows(env, models):
    for model in models:
        env[model].sudo().recompute_all_next_approvers()


def update_flows(browselist):
    update_model_flows(browselist.env, get_applicable_models(browselist))


class ExtendedApprovalConfigMixin(models.AbstractModel):
    _name = "extended.approval.config.mixin"

    def write(self, values):
        r = super(ExtendedApprovalConfigMixin, self).write(values)
        update_flows(self)
        return r

    @api.model
    def create(self, values):
        r = super(ExtendedApprovalConfigMixin, self).create(values)
        update_flows(r)
        return r

    def unlink(self):
        models = get_applicable_models(self)
        r = super(ExtendedApprovalConfigMixin, self).unlink()
        update_model_flows(self.env, models)
        return r
