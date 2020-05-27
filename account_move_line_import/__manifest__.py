# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Import",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "website": "http://www.noviat.com",
    "category": "Accounting & Finance",
    "summary": "Import Accounting Entries",
    "depends": ["account"],
    "external_dependencies": {"python": ["xlrd"]},
    "data": ["views/account_move_views.xml", "wizards/import_move_line_wizard.xml"],
    "installable": True,
}
