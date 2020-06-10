# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Advanced Bank Statement",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "website": "http://www.noviat.com",
    "category": "Accounting & Finance",
    "summary": "Advanced Bank Statement",
    "depends": ["base_iban", "account_menu"],
    "data": [
        "security/ir.model.access.csv",
        "security/account_bank_statement_line_global_security.xml",
        "data/ir_sequence.xml",
        "views/account_bank_statement_views.xml",
        "views/account_bank_statement_line_views.xml",
        "views/account_bank_statement_line_global_views.xml",
        "views/report_statement_balance_report.xml",
        "wizards/bank_statement_balance_print.xml",
        "wizards/bank_statement_automatic_reconcile_result_view.xml",
        "report/statement_balance_report.xml",
    ],
    "installable": True,
}
