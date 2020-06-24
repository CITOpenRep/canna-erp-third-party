# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Extended Approval",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Onestein, Noviat",
    "category": "base",
    "depends": ["base", "account"],  # necessary for menu placement
    "data": ["views/base_extended_approval.xml", "security/ir.model.access.csv"],
    "installable": True,
}
