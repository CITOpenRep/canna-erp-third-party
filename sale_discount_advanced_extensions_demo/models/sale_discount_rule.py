# Copyright (C) 2019-2020 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleDiscountRule(models.Model):
    _inherit = "sale.discount.rule"

    @api.model
    def _selection_matching_type(self):
        res = super()._selection_matching_type()
        return res + [("pallet", "Pallet")]

    @api.model
    def _selection_matching_extra(self):
        res = super()._selection_matching_extra()
        return res + [("extra", "Extra")]

    def _matching_type_methods(self):
        methods = super()._matching_type_methods()
        methods["pallet"] = "_pallet_matching"
        return methods

    def _matching_extra_methods(self):
        methods = super()._matching_extra_methods()
        methods["extra"] = "_extra_matching"
        return methods

    def _pallet_matching(self, lines):
        _logger.warn("_pallet_matching for rule %s, lines=%s", self, lines)
        return True

    def _extra_matching(self, lines):
        _logger.warn("_extra_matching for rule %s, lines=%s", self, lines)
        return True
