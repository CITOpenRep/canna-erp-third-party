# Copyright 2019-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Group Invoice",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "category": "Sales",
    "depends": ["sale_order_group"],
    "data": [
        "views/sale_order_group_views.xml",
        "wizards/sale_order_group_invoice_create.xml",
    ],
    "installable": True,
}
