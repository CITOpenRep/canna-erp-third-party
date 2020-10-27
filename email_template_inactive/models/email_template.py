# Copyright 2009-2017 Noviat.
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    active = fields.Boolean(default=True)
