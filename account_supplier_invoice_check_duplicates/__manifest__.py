# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Supplier Invoice - Check Duplicates",
    "version": "13.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.noviat.com",
    "author": "Noviat",
    "license": "AGPL-3",
    "complexity": "normal",
    "summary": "Supplier Invoice - Check Duplicates",
    "data": ["views/account_move_views.xml"],
    "depends": ["account"],
    "excludes": ["account_invoice_supplier_ref_unique"],
    "installable": True,
}
