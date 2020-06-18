# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Visit",
    "version": "13.0.1.0.0",
    "website": "https://www.onestein.eu",
    "license": "AGPL-3",
    "category": "Sales/CRM",
    "summary": "",
    "author": "Onestein BV, Serpent Consulting Services Pvt. Ltd.",
    "depends": ["base", "mail"],
    "data": [
        "security/crm_visit_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/crm_visit_feeling_views.xml",
        "views/crm_visit_reason_views.xml",
        "views/crm_visit_views.xml",
        "views/res_partner_views.xml",
    ],
}
