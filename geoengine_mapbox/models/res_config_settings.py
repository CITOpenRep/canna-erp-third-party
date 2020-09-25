# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_geoengine_mapbox = fields.Boolean("Enable MapBox for Geo Engine?")
    mapbox_client_id = fields.Char(
        string="Mapbox Client ID", config_parameter="mapbox.client_id"
    )
    feedback_email = fields.Char(
        string="Feedback Email", config_parameter="mapbox.feedback_email"
    )
