# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Price Catalog Purchase",
    "summary": "Catalog Style Pricelists for Purchases",
    "version": "13.0.1.0.0",
    "category": "Operations/Purchase",
    "website": "https://onestein.nl/",
    "author": "Onestein B.V., Noviat",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase", "price_catalog"],
    "data": [
        "views/purchase_order_views.xml",
        "views/price_catalog_views.xml",
        "views/res_partner_views.xml",
        "views/menu.xml",
    ],
}
