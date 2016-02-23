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
from urlparse import urljoin
from urllib import urlencode

from openerp import models, fields, api, _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


class CrmVisit(models.Model):
    _name = "crm.visit"
    _inherit = ["mail.thread"]
    _description = "Visits"
    _order = "date desc"
    _track = {
        'state': {
            'crm_visit.mail_message_subtype_crm_visit_state': lambda self, cr, uid, obj, ctx=None: obj.state in [
                'draft',
                'planned',
                'report',
                'cancel',
                'done'
            ]
        }
    }
    name = fields.Char(
            string="Number",
            readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", _("New Appointment")),
            ("planned", _("Planned Appointment")),
            ("report", _("Needs Report")),
            ("cancel", _("Cancelled")),
            ("done", _("Done")),
        ],
        string="State",
        default='draft',
        track_visibility='onchange',
        readonly=True
    )
    company_id = fields.Many2one(
            comodel_name='res.company',
            string='Company',
            required=True,
            default=lambda self: self.env['res.company']._company_default_get('crm.visit')
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Employee',
        required=True,
        default=lambda self: self.env.user,
        states={'draft' : [("readonly", False)]}
    )
    date = fields.Datetime(
        string="Visit Datetime",
        required=True,
        readonly=True, states={
                "draft": [("readonly", False)],
                "visited": [("readonly", False)]
            }
    )
    duration = fields.Integer(
        string="Duration",
        readonly=True, states={
                "draft" : [("readonly", False)],
                "visited" : [("readonly", False)]
            },
        help="Estimated duration of the visit in minutes"
    )
    reason = fields.Many2one(
        comodel_name="crm.visit.reason",
        string="Reason",
        required=True,
        readonly=True, states={"draft": [("readonly", False)]}
    )
    reason_details = fields.Text(
        string="Purpose",
        readonly=True, states={"draft": [("readonly", False)]}
    )
    feeling = fields.Many2one(
        comodel_name="crm.visit.feeling",
        string="Feeling",
        readonly=True, states={"visited": [("readonly", False)]}
    )
    report = fields.Html(
        string="Report",
        readonly=True,
        required=False, states={"visited": [("readonly", False), ("required", True)]}
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True, states={"draft": [("readonly", False)]}
    )
    main_partner_id = fields.Many2one(
            compute="_get_main_partner_id",
            comodel_name='res.partner',
            string='Main Partner'
    )

    @api.one
    @api.depends('partner_id')
    def _get_main_partner_id(self):
        if self.partner_id.parent_id:
            self.main_partner_id = self.partner_id.parent_id
        else:
            self.main_partner_id = self.partner_id

    @api.model
    def create(self, vals):
        """
        This creates a new visitor.report object, and adds any information that is placed
        in read only fields. Readonly fields don"t get send to the server, so we retreive
        those fields from previous visits.
        :param vals:
        :return:
        """
        vals["name"] = self.env['ir.sequence'].get("crm.visit")

        return super(CrmVisit, self).create(vals)

    @api.one
    def action_confirm(self):
        self.state = "planned"

    @api.one
    def action_edit(self):
        self.state = "draft"

    @api.one
    def action_process(self):
        self.state = "report"

    @api.one
    def action_done(self):
        self.state = "done"

    @api.one
    def action_correct(self):
        self.state = "report"