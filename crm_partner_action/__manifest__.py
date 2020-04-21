# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Partner Action",
    "version": "13.0.1.0.0",
    "website": "https://www.onestein.eu",
    "license": "AGPL-3",
    "category": "CRM",
    "summary": "Register Action to do for partners",
    "author": "Onestein BV, André Schenkels, " "Serpent Consulting Services Pvt. Ltd.",
    "depends": ["base", "mail", "crm_visit", "sale",],
    "data": [
        "security/crm_partner_action_security.xml",
        "security/ir.model.access.csv",
        "views/menu_item.xml",
        "views/mail_message_subtype.xml",
        "views/crm_partner_action_group.xml",
        "views/crm_partner_action.xml",
        "views/res_partner.xml",
        "data/crm_partner_action_sequence.xml",
    ],
}
