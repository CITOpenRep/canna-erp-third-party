# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Operating Unit in CRM Visit",
    "version": "13.0.1.0.0",
    "author": "Onestein BV, Serpent Consulting Services Pvt. Ltd.",
    "license": "AGPL-3",
    "website": "http://www.onestein.eu",
    "category": "CRM",
    "depends": ["crm_visit", "operating_unit"],
    "data": [
        "security/crm_visit_security.xml",
        "security/crm_visit_feeling_security.xml",
        "security/crm_visit_reason_security.xml",
        "views/crm_visit_views.xml",
        "views/crm_visit_feeling_views.xml",
        "views/crm_visit_reason_views.xml",
    ],
}
