# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "account tax code",
    "version": "13.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": """
        Add 'code' field to taxes
    """,
    "author": "Noviat",
    "website": "https://www.noviat.com",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/account_tax_views.xml",
        "views/account_tax_template_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
