# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Intrastat Product Declaration for Belgium",
    "version": "13.0.1.0.0",
    "category": "Intrastat",
    "license": "AGPL-3",
    "summary": "Intrastat Product Declaration for Belgium",
    "author": "Noviat",
    "depends": [
        "intrastat_product",
        # TOOD: restore stock_picking_invoice_link after
        # merge of https://github.com/OCA/stock-logistics-workflow/pull/622
        # "stock_picking_invoice_link",
        "l10n_be_partner_kbo_bce",
    ],
    "conflicts": ["l10n_be_intrastat", "report_intrastat"],
    "data": [
        "security/intrastat_security.xml",
        "security/ir.model.access.csv",
        "data/intrastat_region.xml",
        "data/intrastat_transaction.xml",
        "views/account_move_views.xml",
        "views/intrastat_installer_views.xml",
        "views/l10n_be_intrastat_product_views.xml",
    ],
    "installable": True,
}
