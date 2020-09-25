# Copyright 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import urllib.parse

import pycountry

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

try:
    import requests
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("requests is not available in the sys path")

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = "res.partner"

    date_localization = fields.Datetime(string="Geolocation Date")
    partner_latitude = fields.Float(tracking=True)
    partner_longitude = fields.Float(tracking=True)
    mapbox_error = fields.Text()

    def send_mapbox_fail_mail(self, error):
        template = self.env.ref("geoengine_mapbox.email_template_mapbox_call_fail")
        feedback_email = (
            self.env["ir.config_parameter"].sudo().get_param("mapbox.feedback_email")
        )
        for partner in self:
            partner.write({"mapbox_error": error})
            template.write({"email_to": feedback_email})
            template.send_mail(partner, force_send=False)

    @api.model
    def get_mapbox_client_id(self):
        return self.env["ir.config_parameter"].sudo().get_param("mapbox.client_id")

    def get_mapbox_location(self):
        try:
            mapbox_client_id = self.get_mapbox_client_id()
            access_token = "access_token=" + mapbox_client_id
            url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"

            for partner in self:
                url += urllib.parse.quote(partner.street or "") + ","
                url += urllib.parse.quote(partner.street2 or "") + ","
                url += urllib.parse.quote(partner.city or "") + ","
                url += urllib.parse.quote(partner.zip or "") + ","
                url += (
                    urllib.parse.quote(partner.state_id.name or "" + ",")
                    if partner.state_id
                    else ""
                )
                url_country = ""
                if partner.country_id:
                    country_code = pycountry.countries.get(name=partner.country_id.name)
                    if country_code:
                        url_country = "country=%s&" % (country_code.alpha_2)
                url += ".json?" + url_country
                url += "autocomplete=false&"
                url += access_token
                request_result = requests.get(url)
                try:
                    request_result.raise_for_status()
                except Exception as e:
                    _logger.exception("Geocoding error")
                    raise exceptions.UserError(_("Geocoding error. \n %s") % str(e))
                vals = request_result.json() or {}
                vals = vals and vals.get("features")[0] or {}
                partner.write(
                    {
                        "partner_latitude": vals.get("center")[0] or 0,
                        "partner_longitude": vals.get("center")[1] or 0,
                        "date_localization": fields.Datetime.now(),
                    }
                )
        except Exception as e:
            # Get the latitude and longitude by requesting the "Nominatim"
            # search engine from "openstreetmap". See:
            # https://nominatim.org/release-docs/latest/api/Overview/
            url = "http://nominatim.openstreetmap.org/search"
            headers = {"User-Agent": "Odoobot/13.0.1.0.0 (OCA-geospatial)"}
            for partner in self:
                partner.send_mapbox_fail_mail(e)
                pay_load = {
                    "limit": 1,
                    "format": "json",
                    "street": partner.street or "",
                    "postalCode": partner.zip or "",
                    "city": partner.city or "",
                    "state": partner.state_id and partner.state_id.name or "",
                    "country": partner.country_id and partner.country_id.name or "",
                    "countryCodes": partner.country_id
                    and partner.country_id.code
                    or "",
                }

                request_result = requests.get(url, params=pay_load, headers=headers)
                try:
                    request_result.raise_for_status()
                except Exception as e:
                    _logger.exception("Geocoding error")
                    raise exceptions.UserError(_("Geocoding error. \n %s") % str(e))
                vals = request_result.json()
                vals = vals and vals[0] or {}
                partner.write(
                    {
                        "partner_latitude": vals.get("lat"),
                        "partner_longitude": vals.get("lon"),
                        "date_localization": fields.Datetime.now(),
                    }
                )
