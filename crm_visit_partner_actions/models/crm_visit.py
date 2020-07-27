# OpenERP, Open Source Management Solution
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmVisit(models.Model):
    _inherit = "crm.visit"

    partner_actions = fields.One2many(related="partner_id.actions",
                                      string="Actions",
                                      readonly=False)
