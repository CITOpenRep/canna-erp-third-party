# Copyright 2019-2020 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Group",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat,Serpent Consulting Services Pvt. Ltd.",
    "category": "Sales",
    "depends": ["sale"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/sale_order_group_security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/sale_order_group_views.xml",
        "wizards/sale_order_group_add_order.xml",
        "wizards/sale_order_group_create.xml",
    ],
    "installable": True,
}
