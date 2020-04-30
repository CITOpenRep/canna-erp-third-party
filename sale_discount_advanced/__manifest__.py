# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# Copyright (C) 2020 SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Discount Advanced",
    "author": "ICTSTUDIO,Noviat,Onestein,Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.ictstudio.eu",
    "category": "Sales",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale_apply_price_update"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_message_subtype_data.xml",
        "views/res_partner_views.xml",
        "views/sale_discount_views.xml",
        "views/sale_order_views.xml",
    ],
    "demo": [
        "demo/product_product_demo.xml",
        "demo/sale_discount_demo.xml",
        "demo/sale_discount_rule_demo.xml",
    ],
}
