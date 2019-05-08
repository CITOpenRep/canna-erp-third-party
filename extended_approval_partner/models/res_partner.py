# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'extended.approval.mixin']

    workflow_state_field = 'state'
    workflow_state = 'extended_approval'
    workflow_start_state = 'draft'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('extended_approval', 'Approval'),
            ('confirmed', 'Confirmed')
        ],
        default="draft",
        string='State')

    @api.multi
    def set_state_to_confirmed(self):
        r = self.approve_step()
        if r or self.current_step:
            setattr(
                self,
                self.workflow_state_field,
                self.workflow_state)
            return r
        else:
            self.state = 'confirmed'
