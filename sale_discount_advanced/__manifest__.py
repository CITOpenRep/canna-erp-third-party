# See LICENSE file for full copyright and licensing details.

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
        "data/product_data.xml",
        "views/res_partner_views.xml",
        "views/sale_discount_views.xml",
        "views/sale_order_views.xml",
    ],
    "demo": ["demo/sale_discount.xml", "demo/sale_discount_rule.xml"],
}
