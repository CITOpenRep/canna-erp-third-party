# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_group_id = fields.Many2many(
        comodel_name='sale.order.group',
        relation='sale_order_group_rel',
        column1='order_id',
        column2='group_id',
        string='Sale Order Group',
        copy=False)

    @api.multi
    def action_button_confirm(self):
        self.ensure_one()
        if (not self.env.context.get('confirm_from_group') and
                self.sale_order_group_id):
            raise UserError(_(
                "This order belongs to a Sale Order Group.\n"
                "Please open the group to confirm all orders "
                "in this group."
            ))
        else:
            return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def action_cancel(self):
        if not self.env.context.get('cancel_from_group'):
            for so in self:
                if so.sale_order_group_id:
                    raise UserError(_(
                        "Order '%s' belongs to a Sale Order Group.\n"
                        "Please open the group to cancel all orders "
                        "in this group."
                    ) % so.name)
        return super(SaleOrder, self).action_cancel()
