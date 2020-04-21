# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)


class CrmPartnerActionGroup(models.Model):
    _name = "crm.partner.action.group"
    _description = "Action Group"

    name = fields.Char(string="Name of the Group", size=80, required=True)
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Related Model",
        help="If possible, a warning will be shown "
        "when creating an object of this "
        "model and there are open actions "
        "for this group",
    )
    # '_company_default_get' on res.company is deprecated and shouldn't be used
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
