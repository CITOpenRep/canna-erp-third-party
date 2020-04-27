# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Extended Approval",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Onestein," " Serpent Consulting Services Pvt. Ltd.",
    "category": "base",
    "depends": [
        "base",
        "account",  # necessary for menu placement
        "base_automation",  # necessary for base action rule.
    ],
    "data": ["views/base_extended_approval.xml", "security/ir.model.access.csv"],
    "installable": True,
}
