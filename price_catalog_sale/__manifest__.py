# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Price Catalog Sale",
    "summary": "Catalog Style Pricelists for Sales",
    "version": "13.0.0.0.1",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://onestein.nl/",
    "author": "Onestein B.V.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management", "price_catalog"],
    "data": [
        "views/sale_order_views.xml",
        "views/price_catalog_views.xml",
        "views/res_partner_views.xml",
        "views/menu.xml",
    ],
}
