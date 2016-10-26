# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Onestein BV (www.onestein.eu).
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

import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class CrmPartnerAction(models.Model):
    _name = 'crm.partner.action'
    _inherit = ['mail.thread']
    _description = 'Crm Actions'
    _order = 'create_date desc'
    _track = {
        'state': {
            'crm_partner_action.mail_message_subtype_crm_partner_action_state': lambda
                self, cr, uid, obj, ctx=None: obj.state in [
                'open',
                'done'
            ]
        },
    }

    name = fields.Char(
        string='Number',
        readonly=True
    )
    color = fields.Integer(
        string='Color Index'
    )
    state = fields.Selection(
        selection=[
            ('open', _('Open')),
            ('done', _('Done')),
        ],
        string='State',
        default='open',
        readonly=True,
        track_visibility='onchange'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        # default=lambda self: self.env['res.company']._company_default_get('crm.partner.action')
        default=lambda self: self.env['res.company'].browse(
            self.env['res.company']._company_default_get(
                'crm.partner.action'))
        # default=1,
        # TODO kng: comment and uncomment    default=1. Not working for migration
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=False,
        default=lambda self: self.env.user,
        help="Pick a user who will receive a notification when choosing the"
             " partner selected above on a Sale Order. Leave empty to have"
             " everyone receive the notification."
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        readonly=True, states={'open': [('readonly', False)]}
    )
    followup_date = fields.Date(
        string='Follow Up Date',
        help="This Action needs follow up before this date."
    )
    followup_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Follow Up User',
        help='User who is going to take this action.',
        default=lambda self: self.env.user,
        readonly=True, states={'open': [('readonly', False)]}
    )
    action_group_id = fields.Many2one(
        comodel_name='crm.partner.action.group',
        string='Group',
        help="The group of users this action is meant for.",
        readonly=True, states={'open': [('readonly', False)]}
    )
    main_partner_id = fields.Many2one(
        compute="_get_main_partner_id",
        comodel_name='res.partner',
        string='Main Partner'
    )
    description = fields.Text(
        string='Description',
        required=True,
        # readonly=True, states={'open': [('readonly', False)]} TODO: Move to view
    )
    comments = fields.Text(
        string='Comments',
        readonly=True, states={'open': [('readonly', False)]}
    )

    @api.one
    @api.depends('partner_id')
    def _get_main_partner_id(self):
        if self.partner_id.parent_id:
            self.main_partner_id = self.partner_id.parent_id
        else:
            self.main_partner_id = self.partner_id

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_open(self):
        self.state = 'open'

    @api.model
    def create(self, vals):
        """
        This creates a new visitor.report object, and adds any information that is placed
        in read only fields. Readonly fields don"t get send to the server, so we retreive
        those fields from previous visits.
        :param vals:
        :return:
        """
        vals["name"] = self.env['ir.sequence'].get("crm.partner.action")

        return super(CrmPartnerAction, self).create(vals)
