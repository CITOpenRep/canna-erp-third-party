# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmVisitFeeling(models.Model):
    _name = "crm.visit.feeling"
    _description = "Visit feeling"

    name = fields.Char(string="Feeling", size=80, required=True, translate=True)
    active = fields.Boolean(default=True)
    # '_company_default_get' on res.company is deprecated and shouldn't be used
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
