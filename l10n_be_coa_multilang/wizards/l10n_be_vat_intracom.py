# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging

from lxml import etree

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import translate

_logger = logging.getLogger(__name__)

IR_TRANSLATION_NAME = "l10n.be.vat.intracom"


class L10nBeVatIntracom(models.TransientModel):
    _name = "l10n.be.vat.intracom"
    _inherit = "l10n.be.vat.common"
    _description = "Intracom VAT Declaration"

    # result view fields
    client_ids = fields.One2many(
        comodel_name="l10n.be.vat.intracom.client",
        inverse_name="intracom_id",
        string="Clients",
    )

    def generate_declaration(self):
        self.ensure_one()
        client_vals = self._get_client_vals()
        self.client_ids = [(0, 0, x) for x in client_vals]

        module = __name__.split("addons.")[1].split(".")[0]
        result_view = self.env.ref(
            "{}.{}_view_form_declaration".format(module, self._table)
        )

        return {
            "name": _("Intracom VAT Declaration"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "target": "inline",
            "view_id": result_view.id,
            "type": "ir.actions.act_window",
        }

    def create_xls(self):
        report_file = "vat_intra_%s" % self.period
        module = __name__.split("addons.")[1].split(".")[0]
        report_name = "{}.vat_intracom_xls".format(module)
        report = {
            "name": _("Intracom VAT Declaration"),
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "report_file": report_name,
            "context": dict(self.env.context, report_file=report_file),
            "data": {"dynamic_report": True},
        }
        return report

    def create_xml(self):
        """
        Intervat XML Periodical VAT Declaration.
        TODO: add support for 'Representative' (Mandataris)
        """

        ns_map = {
            None: "http://www.minfin.fgov.be/IntraConsignment",
            "ic": "http://www.minfin.fgov.be/InputCommon",
        }

        Doc = etree.Element(
            "IntraConsignment", attrib={"IntraListingsNbr": "1"}, nsmap=ns_map
        )

        # self._node_Representative(Doc, ns_map)
        ref = self._get_declaration_ref()
        # self._node_RepresentativeReference(Doc, ns_map, ref)

        self._node_IntraListing(Doc, ns_map, ref)

        xml_string = etree.tostring(
            Doc, pretty_print=True, encoding="ISO-8859-1", xml_declaration=True
        )

        self._validate_xmlschema(xml_string, "NewICO-in_v0_9.xsd")
        self.file_name = "vat_intra_%s.xml" % self.period
        self.file_save = base64.encodestring(xml_string)

        return self._action_save_xml()

    def print_declaration(self):
        module = __name__.split("addons.")[1].split(".")[0]
        return self.env.ref(
            "%s.action_report_l10nbevatintracom" % module
        ).report_action(self)

    def _get_client_vals(self):
        flds = ["partner_id", "debit", "credit"]
        groupby = ["partner_id"]

        aml_dom = self._get_move_line_date_domain()
        S_dom, L_dom, T_dom = self._get_move_line_tax_domains()
        S_data = self.env["account.move.line"].read_group(
            aml_dom + S_dom, flds, groupby
        )
        for entry in S_data:
            entry["code"] = "S"
        L_data = self.env["account.move.line"].read_group(
            aml_dom + L_dom, flds, groupby
        )
        for entry in L_data:
            entry["code"] = "L"
        T_data = self.env["account.move.line"].read_group(
            aml_dom + T_dom, flds, groupby
        )
        for entry in T_data:
            entry["code"] = "T"

        records = {}
        for entry in S_data + L_data + T_data:
            partner = self.env["res.partner"].browse(entry["partner_id"][0])
            vat = self._normalise_vat(partner.vat)
            if vat in records:
                records[vat].append(
                    {
                        "partner_id": partner.id,
                        "vat": vat,
                        "code": entry["code"],
                        "amount": entry["credit"] - entry["debit"],
                    }
                )
            else:
                records[vat] = [
                    {
                        "partner_id": partner.id,
                        "vat": vat,
                        "code": entry["code"],
                        "amount": entry["credit"] - entry["debit"],
                    }
                ]

        ic_vals = []
        for k in records:
            ic_vals += records[k]
        ic_vals.sort(key=lambda k: k["vat"])
        return ic_vals

    def _get_move_line_tax_domains(self):

        dom = [
            ("country_id", "=", self.env.ref("base.be").id),
            ("applicability", "=", "taxes"),
        ]
        code_S = "44"
        dom_S = dom + [("name", "=", "+" + code_S)]
        tags_S = self.env["account.account.tag"].search(dom_S)
        S_dom = [("tag_ids.id", "in", tags_S.ids)]

        code_L = "46L"
        dom_L = dom + [("name", "=", "+" + code_L)]
        tags_L = self.env["account.account.tag"].search(dom_L)
        L_dom = [("tag_ids.id", "in", tags_L.ids)]

        code_T = "46T"
        dom_T = dom + [("name", "=", "+" + code_T)]
        tags_T = self.env["account.account.tag"].search(dom_T)
        T_dom = [("tag_ids.id", "in", tags_T.ids)]

        return S_dom, L_dom, T_dom

    def _get_intra_list(self):
        intra_list = {}
        for client in self.client_ids:
            vat = client.vat
            if vat == "-":
                raise UserError(
                    _("Missing VAT number for partner '%s'") % client.partner_id.name
                )
            key = "{}-{}".format(vat, client.code)
            if key in intra_list:
                intra_list[key]["amount"] += client.amount
            else:
                intra_list[key] = {
                    "vat": client.vat,
                    "code": client.code,
                    "amount": client.amount,
                }
        for k in list(intra_list.keys()):
            if not intra_list[k]["amount"]:
                del intra_list[k]
        return intra_list

    def _node_IntraListing(self, parent, ns_map, ref):
        intra_list = self._get_intra_list()
        AmountSum = sum([x["amount"] for x in list(intra_list.values())])
        ClientsNbr = len(intra_list)
        if not ClientsNbr:
            raise UserError(_("No Intracom transactions found for %s.") % self.period)

        IntraListing = etree.SubElement(
            parent,
            "IntraListing",
            attrib={
                "SequenceNumber": "1",
                "ClientsNbr": "%s" % ClientsNbr,
                "DeclarantReference": ref,
                "AmountSum": "%.2f" % AmountSum,
            },
        )

        # ReplacedIntraListing not supported at this point in time
        # TODO:
        # Create object to save legal VAT declarations in order to
        # and add support of replacements.
        # self._node_ReplacedIntraListing(IntraListing, ns_map, replace_ref)

        self._node_Declarant(IntraListing, ns_map)
        self._node_Period(IntraListing, ns_map)

        seq = 1
        for k in intra_list:
            client = {
                "vat": intra_list[k]["vat"],
                "code": intra_list[k]["code"],
                "amount": intra_list[k]["amount"],
            }
            self._node_IntraClient(IntraListing, ns_map, client, seq)
            seq += 1

        # TODO: add support for attachments
        # self._node_FileAttachment(parent, ns_map)

        self._node_Comment(IntraListing, ns_map)

    def _node_IntraClient(self, IntraListing, ns_map, client, seq):
        IntraClient = etree.SubElement(
            IntraListing, "IntraClient", attrib={"SequenceNumber": str(seq)}
        )

        CompanyVATNumber = etree.SubElement(
            IntraClient, "CompanyVATNumber", attrib={"issuedBy": client["vat"][:2]}
        )
        CompanyVATNumber.text = client["vat"][2:]

        Code = etree.SubElement(IntraClient, "Code")
        Code.text = client["code"]

        Amount = etree.SubElement(IntraClient, "Amount")
        Amount.text = "%.2f" % client["amount"]

        # CorrectingPeriod not supported at this point in time
        # CorrectingPeriod = etree.SubElement(
        #     IntraClient, 'CorrectingPeriod')


class L10nBeVatIntracomClient(models.TransientModel):
    _name = "l10n.be.vat.intracom.client"
    _description = "Intracom VAT Declaration line"

    intracom_id = fields.Many2one(
        comodel_name="l10n.be.vat.intracom", string="Intracom VAT Declaration"
    )
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=1)
    vat = fields.Char(string="VAT Number", readonly=1)
    code = fields.Selection(selection=[("L", "L"), ("S", "S"), ("T", "T")], readonly=1)
    amount = fields.Monetary(string="Amount", currency_field="currency_id", readonly=1)
    currency_id = fields.Many2one(related="intracom_id.currency_id", readonly=1)

    def view_move_lines(self):
        self.ensure_one()
        act_window = self.intracom_id._move_lines_act_window()
        aml_dom = self.intracom_id._get_move_line_date_domain()
        aml_dom += [("partner_id", "=", self.partner_id.id)]
        tax_doms = self.intracom_id._get_move_line_tax_domains()
        i = ["S", "L", "T"].index(self.code)
        act_window["domain"] = aml_dom + tax_doms[i]
        return act_window


class L10nBeVatIntracomXlsx(models.AbstractModel):
    _name = "report.l10n_be_coa_multilang.vat_intracom_xls"
    _inherit = "report.report_xlsx.abstract"
    _description = "Intracom declaration excel export"

    def _(self, src):
        lang = self.env.context.get("lang", "en_US")
        val = translate(self.env.cr, IR_TRANSLATION_NAME, "report", lang, src) or src
        return val

    def _get_ws_params(self, workbook, data, listing):

        col_specs = {
            "seq": {
                "header": {"value": self._("Nr")},
                "lines": {"value": self._render("str(seq)")},
                "width": 5,
            },
            "vat": {
                "header": {"value": self._("VAT Number")},
                "lines": {"value": self._render("c.vat")},
                "width": 18,
            },
            "partner": {
                "header": {"value": self._("Partner")},
                "lines": {"value": self._render("c.partner_id.name")},
                "width": 52,
            },
            "code": {
                "header": {
                    "value": self._("Code"),
                    "format": self.format_theader_yellow_center,
                },
                "lines": {
                    "value": self._render("c.code"),
                    "format": self.format_tcell_center,
                },
                "width": 5,
            },
            "amount": {
                "header": {
                    "value": self._("Amount"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("c.amount"),
                    "format": self.format_tcell_amount_right,
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("total_amount_formula"),
                    "format": self.format_theader_yellow_amount_right,
                },
                "width": 18,
            },
        }
        wanted_list = ["seq", "vat", "partner", "code", "amount"]

        return [
            {
                "ws_name": "vat_intra_%s" % listing.period,
                "generate_ws_method": "_generate_listing",
                "title": listing._description,
                "wanted_list": wanted_list,
                "col_specs": col_specs,
            }
        ]

    def _generate_listing(self, workbook, ws, ws_params, data, listing):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._listing_title(ws, row_pos, ws_params, data, listing)
        row_pos = self._listing_info(ws, row_pos, ws_params, data, listing)
        row_pos = self._listing_lines(ws, row_pos, ws_params, data, listing)

    def _listing_title(self, ws, row_pos, ws_params, data, listing):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _listing_info(self, ws, row_pos, ws_params, data, listing):
        ws.write_string(row_pos, 1, self._("Company") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, listing.company_id.name)
        row_pos += 1
        ws.write_string(row_pos, 1, self._("VAT Number") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, listing.company_id.vat or "")
        row_pos += 1
        ws.write_string(row_pos, 1, self._("Period") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, listing.period)
        return row_pos + 2

    def _listing_lines(self, ws, row_pos, ws_params, data, listing):

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_yellow_left,
        )

        ws.freeze_panes(row_pos, 0)

        seq = 1
        row_pos_start = row_pos
        previous_client = False
        for c in listing.client_ids:
            if seq > 1:
                if c.vat == previous_client.vat:
                    seq -= 1
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="lines",
                render_space={"seq": seq, "c": c},
                default_format=self.format_tcell_left,
            )
            seq += 1
            previous_client = c

        amount_pos = ws_params["wanted_list"].index("amount")
        amount_start = self._rowcol_to_cell(row_pos_start, amount_pos)
        amount_stop = self._rowcol_to_cell(row_pos - 1, amount_pos)
        total_amount_formula = "SUM({}:{})".format(amount_start, amount_stop)
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={"total_amount_formula": total_amount_formula},
            default_format=self.format_theader_yellow_left,
        )

        return row_pos + 1
