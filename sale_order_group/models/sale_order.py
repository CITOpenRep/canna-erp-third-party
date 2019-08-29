# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_group_id = fields.Many2one(
        comodel_name='sale.order.group',
        string='Sale Order Group',
        ondelete='set null',
        copy=False)
    sale_order_group_state = fields.Selection(
        related='sale_order_group_id.state',
        string='Sale Order Group State')

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

    @api.multi
    def remove_from_sale_order_group(self):
        for so in self:
            so.sale_order_group_id = False
        return True
