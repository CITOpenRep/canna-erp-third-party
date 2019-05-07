# -*- coding: utf-8 -*-
# Copyright 2019 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rules = env['sale.discount.rule'].search([])
    for rule in rules:
        if rule.product_category_id:
            rule.product_category_ids |= rule.product_category_id
        if rule.product_id:
            rule.product_ids |= rule.product_id
