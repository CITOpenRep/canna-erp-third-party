# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, models


class PurchaseOrder(models.Model):
    """
    ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    """
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'extended.approval.workflow.mixin']

    workflow_signal = 'purchase'
    workflow_start_state = 'draft'
    workflow_idx_state = 'purchase'

    def action_cancel(self):
        self.cancel_approval()
        return super(PurchaseOrder, self).action_cancel()
