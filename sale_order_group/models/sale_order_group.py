# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models


class SaleOrderGroup(models.Model):
    _name = 'sale.order.group'

    name = fields.Char(
        string='Order Group Reference',
        required=True, copy=False, readonly=True,
        default=lambda self: self._default_name())
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled')],
        readonly=True, default='draft')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True)
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        relation='sale_order_group_rel',
        column1='group_id',
        column2='order_id',
        domain="[('state', 'in', ['draft', 'sent']),"
               " ('partner_id.commercial_partner_id', '=', partner_id)]",
        string='Orders',
        copy=False)

    @api.model
    def _default_name(self):
        return self.env['ir.sequence'].next_by_code('sale.order.group')

    @api.multi
    def button_confirm(self):
        ctx = dict(self.env.context, confirm_from_group=True)
        for so in self.sale_order_ids.with_context(ctx):
            so.action_button_confirm()
        self.state = 'confirm'
        return True

    @api.multi
    def button_cancel(self):
        ctx = dict(self.env.context, cancel_from_group=True)
        res = self.sale_order_ids.with_context(ctx).action_cancel()
        self.state = 'cancel'
        return res
