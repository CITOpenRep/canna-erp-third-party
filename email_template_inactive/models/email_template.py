# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    active = fields.Boolean(select=True, default=True)
