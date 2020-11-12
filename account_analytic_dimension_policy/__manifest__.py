# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Dimension Policy",
    "version": "13.0.1.1.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "category": "Accounting & Finance",
    "depends": ["account"],
    "data": [
        "data/ir_property_data.xml",
        "views/account_account_type_views.xml",
        "views/account_account_views.xml",
        "views/account_group_views.xml",
        "views/account_move_views.xml",
        "views/account_move_line_views.xml",
        "views/assets_backend.xml",
    ],
    "installable": True,
}
