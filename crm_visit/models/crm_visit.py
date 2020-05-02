# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmVisit(models.Model):
    _name = "crm.visit"
    _inherit = ["mail.thread", "portal.mixin", "mail.activity.mixin"]
    _description = "Visits"
    _order = "date desc"

    name = fields.Char(string="Number", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("planned", "Appointment"),
            ("visited", "Needs Report"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
        readonly=True,
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
        string="Employee",
        required=True,
        default=lambda self: self.env.user,
    )
    date = fields.Datetime(string="Visit Datetime", required=True, readonly=True)
    duration = fields.Integer(
        string="Duration",
        readonly=True,
        help="Estimated duration of the " "visit in minutes",
    )
    visit_reason = fields.Many2one(
        comodel_name="crm.visit.reason", string="Reason", required=True, readonly=True
    )
    visit_reason_details = fields.Text(string="Purpose", readonly=True)
    visit_feeling = fields.Many2one(
        comodel_name="crm.visit.feeling", string="Feeling", readonly=True
    )
    report = fields.Html(string="Report", readonly=True, required=False)
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, readonly=True
    )

    @api.model
    def create(self, vals):
        """
        This creates a new visitor.report object and adds any information
        that is placed in readonly fields.
        Readonly fields don't get send to the server, so we retrieve
        those fields from previous visits.
        """
        vals["name"] = self.env["ir.sequence"].next_by_code("crm.visit")
        return super(CrmVisit, self).create(vals)

    def unlink(self):
        for visit in self:
            if visit.state != "draft":
                raise UserError(_("Only visits in state 'draft'" " can be deleted. "))
        return super(CrmVisit, self).unlink()

    def action_confirm(self):
        self.state = "planned"

    def action_edit(self):
        self.state = "draft"

    def action_process(self):
        self.state = "visited"

    def action_done(self):
        self.state = "done"

    def action_correct(self):
        self.state = "visited"
