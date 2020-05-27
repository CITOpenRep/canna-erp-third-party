# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Level Excel export',
    'version': '12.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Warehouse Management',
    'depends': ['stock', 'report_xlsx_helper'],
    'data': [
        'wizards/wiz_export_stock_level.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
