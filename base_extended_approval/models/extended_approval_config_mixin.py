# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
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
    _description = "Mixin class for extended approval config"

    def write(self, values):
        r = super().write(values)
        update_flows(self)
        return r

    @api.model
    def create(self, values):
        r = super().create(values)
        update_flows(r)
        return r

    def unlink(self):
        models = get_applicable_models(self)
        r = super().unlink()
        update_model_flows(self.env, models)
        return r
