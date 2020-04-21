# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Discount on Payment Terms",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat,Onestein," "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.noviat.com",
    "category": "Sales",
    "depends": ["sale_discount_advanced"],
    "data": [
        "views/account_payment_term_views.xml",
        "views/sale_discount_views.xml",
        "views/sale_order_views.xml",
    ],
    "demo": ["demo/sale_discount.xml"],
    "installable": True,
}
