# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Level import",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "website": "http://www.noviat.com",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "external_dependencies": {"python": ["xlrd"]},
    "data": ["views/stock_inventory_views.xml", "wizards/import_stock_level_views.xml"],
    "installable": True,
}
