# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Price Catalog",
    "summary": "Catalog Style Pricelists",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://onestein.nl/",
    "author": "Onestein B.V., Noviat",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product"],
    "data": [
        "security/price_catalog_security.xml",
        "security/ir.model.access.csv",
        "views/price_subcatalog_views.xml",
        "views/price_catalog_views.xml",
    ],
}
