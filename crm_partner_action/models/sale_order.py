# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 Onestein BV (www.onestein.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def onchange_partner_id(self, cr, uid, ids, partner_id, context):
        partner_action_obj = self.pool.get('crm.partner.action')
        partner_obj = self.pool.get('res.partner')
        res = super(SaleOrder, self).onchange_partner_id(cr, uid, ids,
                                                         partner_id)
        if not partner_id:
            return res
        part = partner_obj.browse(cr, uid, partner_id)
        res['value']['note'] = part.delivery_instructions
        res['value'][
            'user_id'] = uid
        if 'pricelist_id' in res['value'] and res['value']['pricelist_id']:
            if isinstance(res['value']['pricelist_id'], long):
                res['value']['pricelist_id'] = int(res['value']['pricelist_id'])

        search_terms = [('partner_id', '=', part.id), ('state', '=', 'open')]
        action_ids = partner_action_obj.search(cr, uid, search_terms)
        actions = partner_action_obj.browse(cr, uid, action_ids,
                                            context=context)
        action_user_ids = [action.user_id.id for action in actions]
        if action_ids and (
            not any(action_user_ids) or uid in action_user_ids):
            message_body = ''
            for action in partner_action_obj.browse(cr, uid, action_ids):
                if not any(action_user_ids) or uid in action_user_ids:
                    message_body += action.description
                    if action.comments:
                        message_body += '\n\n' + action.comments
                    message_body += '\n\n'

            res['warning'] = {
                'title': _('Open Actions'),
                'message': _(
                    'There are still open actions for this partner. Please check if there are any relevant actions') + '\n\n' + message_body
            }
        return res
