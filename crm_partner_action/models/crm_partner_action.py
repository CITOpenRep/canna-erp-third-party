# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class CrmPartnerAction(models.Model):
    _name = "crm.partner.action"
    _inherit = ["mail.thread", "portal.mixin", "mail.activity.mixin"]
    _description = "Crm Actions"
    _order = "create_date desc"

    name = fields.Char(string="Number", readonly=True)
    color = fields.Integer(string="Color Index")
    state = fields.Selection(
        selection=[("open", _("Open")), ("done", _("Done"))],
        string="State",
        default="open",
        readonly=True,
        track_visibility="onchange",
    )
    # '_company_default_get' on res.company is deprecated and shouldn't be used
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=False,
        default=lambda self: self.env.user,
        help="Pick a user who will receive a "
        "notification when choosing the partner "
        "selected above on a Sale Order. Leave empty to "
        "have everyone receive the notification.",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
        readonly=True,
        states={"open": [("readonly", False)]},
    )
    followup_date = fields.Date(
        string="Follow Up Date", help="This Action needs follow up before " "this date."
    )
    followup_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Follow Up User",
        help="User who is going to take this "
        "action.\n Leave blank to show the "
        "action to all users",
        readonly=True,
        states={"open": [("readonly", False)]},
    )
    action_group_id = fields.Many2one(
        comodel_name="crm.partner.action.group",
        string="Group",
        help="The group of users this action " "is meant for.",
        readonly=True,
        states={"open": [("readonly", False)]},
    )
    main_partner_id = fields.Many2one(
        compute="_get_main_partner_id",
        comodel_name="res.partner",
        string="Main Partner",
    )
    description = fields.Text(string="Description", required=True)
    comments = fields.Text(
        string="Comments", readonly=True, states={"open": [("readonly", False)]}
    )

    @api.depends("partner_id")
    def _get_main_partner_id(self):
        if self.partner_id.parent_id:
            self.main_partner_id = self.partner_id.parent_id
        else:
            self.main_partner_id = self.partner_id

    def action_done(self):
        self.state = "done"

    def action_open(self):
        self.state = "open"

    @api.model
    def create(self, vals):
        """
        This creates a new visitor.report object, and adds any
        information that is placed in read only fields.
        Readonly fields don"t get send to the server, so we retreive
        those fields from previous visits.
        :param vals:
        :return:
        """
        vals["name"] = self.env["ir.sequence"].next_by_code("crm.partner.action")
        return super(CrmPartnerAction, self).create(vals)
