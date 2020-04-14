# Copyright 2019 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from distutils.version import LooseVersion as lversion

from openerp import SUPERUSER_ID, api
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


@openupgrade.migrate(no_version=False)
def migrate(cr, version):
    if lversion(version) < lversion("8.0.2.1.0"):
        # Field product_category_id was added in 2.1.0, so skip if older.
        # For future reference: it was removed in version 3.1.0.
        _logger.info("Skipping module as source version is %s.", version)
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    rules = env["sale.discount.rule"].search([])
    for rule in rules:
        if rule.product_category_id:
            rule.product_category_ids |= rule.product_category_id
        if rule.product_id:
            rule.product_ids |= rule.product_id
