# Copyright 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "GeoEngine MapBox",
    "version": "13.0.1.0.0",
    "category": "GeoBI",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "license": "AGPL-3",
    "website": "https://serpentcs.com",
    "depends": ["geoengine_partner"],
    "external_dependencies": {"python": ["pycountry"]},
    "data": [
        "data/mail_template_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_view.xml",
        "views/template.xml",
    ],
    "installable": True,
    "application": True,
}
