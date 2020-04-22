# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Extended Approval Purchase Order",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Onestein, " "Serpent Consulting Services Pvt. Ltd.",
    "category": "base",
    "depends": ["purchase", "base_extended_approval",],
    "data": [
        "data/email_template_data.xml",
        "data/base_action_rule_data.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
