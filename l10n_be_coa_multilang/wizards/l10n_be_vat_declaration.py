# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
import time

from lxml import etree

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import translate

_logger = logging.getLogger(__name__)

IR_TRANSLATION_NAME = "l10n.be.vat.declaration"


class L10nBeVatDeclaration(models.TransientModel):
    _name = "l10n.be.vat.declaration"
    _inherit = "l10n.be.vat.common"
    _description = "Periodical VAT Declaration"

    ask_restitution = fields.Boolean(
        string="Ask Restitution", help="Request for refund"
    )
    ask_payment = fields.Boolean(string="Ask Payment", help="Request for payment forms")
    client_nihil = fields.Boolean(
        string="Last Declaration, no clients in client listing",
        help="Applies only to the last declaration of the calendar year "
        "or the declaration concerning the cessation of activity:\n"
        "no clients to be included in the client listing.",
    )
    # result view fields
    case_ids = fields.One2many(
        comodel_name="l10n.be.vat.declaration.case",
        inverse_name="declaration_id",
        string="Cases",
    )
    controls = fields.Text()

    def generate_declaration(self):
        self.ensure_one()
        self.note = ""
        case_vals = self._get_case_vals()
        self.case_ids = [(0, 0, x) for x in case_vals]
        self._vat_declaration_controls()
        module = __name__.split("addons.")[1].split(".")[0]
        result_view = self.env.ref(
            "{}.{}_view_form_declaration".format(module, self._table)
        )

        return {
            "name": _("Periodical VAT Declaration"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "target": "inline",
            "view_id": result_view.id,
            "type": "ir.actions.act_window",
        }

    def create_xls(self):
        report_file = "vat_declaration_%s" % self.period
        module = __name__.split("addons.")[1].split(".")[0]
        report_name = "{}.vat_declaration_xls".format(module)
        report = {
            "name": _("Periodical VAT Declaration"),
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "report_file": report_name,
            "context": dict(self.env.context, report_file=report_file),
            "data": {"dynamic_report": True},
        }
        return report

    def create_detail_xls(self):
        report_file = "vat_detail_%s" % self.period
        module = __name__.split("addons.")[1].split(".")[0]
        report_name = "{}.vat_detail_xls".format(module)
        report = {
            "name": _("Periodical VAT Declaration details"),
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
            None: "http://www.minfin.fgov.be/VATConsignment",
            "ic": "http://www.minfin.fgov.be/InputCommon",
        }

        Doc = etree.Element(
            "VATConsignment", attrib={"VATDeclarationsNbr": "1"}, nsmap=ns_map
        )

        # self._node_Representative(Doc, ns_map)
        ref = self._get_declaration_ref()
        # self._node_RepresentativeReference(Doc, ns_map, ref)

        self._node_VATDeclaration(Doc, ns_map, ref)

        xml_string = etree.tostring(
            Doc, pretty_print=True, encoding="ISO-8859-1", xml_declaration=True
        )

        self._validate_xmlschema(xml_string, "NewTVA-in_v0_9.xsd")
        self.file_name = "vat_declaration_%s.xml" % self.period
        self.file_save = base64.encodestring(xml_string)

        return self._action_save_xml()

    def print_declaration(self):
        module = __name__.split("addons.")[1].split(".")[0]
        return self.env.ref(
            "%s.action_report_l10nbevatdeclaration" % module
        ).report_action(self)

    def _intervat_cases(self):
        return [
            "00",
            "01",
            "02",
            "03",
            "44",
            "45",
            "46",
            "47",
            "48",
            "49",
            "54",
            "55",
            "56",
            "57",
            "59",
            "61",
            "62",
            "63",
            "64",
            "71",
            "72",
            "81",
            "82",
            "83",
            "84",
            "85",
            "86",
            "87",
            "88",
            "91",
        ]

    def _get_case_domain(self, case_report):
        if case_report.children_line_ids:
            case_dom = []
            cases = case_report.search(
                [
                    ("parent_id", "child_of", case_report.id),
                    ("children_line_ids", "=", False),
                ]
            )
            for i, case in enumerate(cases, start=1):
                if i != len(cases):
                    case_dom += ["|"]
                case_dom += [("tag_ids", "in", case.tag_ids.ids)]
        else:
            case_dom = [("tag_ids", "in", case_report.tag_ids.ids)]
        return case_dom

    def _calc_parent_case_amounts(self, case, amounts):
        if case.id not in amounts:
            for child in case.children_line_ids:
                if child.id not in amounts:
                    self._calc_parent_case_amounts(child, amounts)
            amounts[case.id] = sum(
                [x.factor * amounts[x.id] for x in case.children_line_ids]
            )

    def _get_case_amounts(self, case_root, tax_code_map):
        cases = case_root.search(
            [("parent_id", "child_of", case_root.id), ("children_line_ids", "=", False)]
        )
        amounts = dict.fromkeys(cases.mapped("id"), 0.0)
        date_dom = self._get_move_line_date_domain()
        min_types = ["out_invoice", "out_receipt", "in_refund"]
        dom_min = [("move_id.type", "in", min_types)]
        dom_plus = [("move_id.type", "not in", min_types)]
        for case in cases:
            tc = case.code
            for tag in tax_code_map[tc]:
                aml_dom = date_dom + [("tag_ids", "in", tag.id)]
                sign = tag.tax_negate and -1 or 1
                flds = ["balance"]
                groupby = []
                amt = self.env["account.move.line"].read_group(
                    aml_dom + dom_plus, flds, groupby
                )[0]
                amounts[case.id] += self.currency_id.round(
                    sign * (amt["balance"] or 0.0)
                )
                amt = self.env["account.move.line"].read_group(
                    aml_dom + dom_min, flds, groupby
                )[0]
                amounts[case.id] += self.currency_id.round(
                    sign * -1 * (amt["balance"] or 0.0)
                )

        self._calc_parent_case_amounts(case_root, amounts)

        return amounts

    def _get_case_child(self, case, level, case_vals, case_amounts):
        case_vals.append(
            {
                "case_id": case.id,
                "level": level,
                "active": not case.invisible,
                "amount": case_amounts.get(case.id, 0.0),
            }
        )
        for child in case.children_line_ids:
            self._get_case_child(child, level + 1, case_vals, case_amounts)

    def _get_tax_code_map(self):
        """
        :return: dict
            key: tax code
            value: list of tags
        """
        tax_tags = (
            self.env["account.account.tag"]
            .with_context(active_test=False)
            .search(
                [
                    ("country_id", "=", self.env.ref("base.be").id),
                    ("applicability", "=", "taxes"),
                ]
            )
        )
        be_tax_codes = self._intervat_cases()
        tax_code_map = {}
        be_tax_tags = self.env["account.account.tag"]
        for tag in tax_tags:
            tc = tag.name[1:]
            if tc[:2] not in be_tax_codes:
                continue
            else:
                be_tax_tags |= tag
                if tc not in tax_code_map:
                    tax_code_map[tc] = tag
                else:
                    tax_code_map[tc] |= tag
        return tax_code_map, tax_tags

    def _get_case_vals(self):
        case_root = self.env["account.tax.report.line"].search(
            [("country_id", "=", self.env.ref("base.be").id), ("parent_id", "=", False)]
        )
        if len(case_root) != 1:
            raise UserError(
                _(
                    "Incorrect Belgian Tax Tag Code Chart."
                    "\nReport this problem via your Odoo support "
                    "partner."
                )
            )

        tax_code_map, tax_tags = self._get_tax_code_map()
        case_amounts = self._get_case_amounts(case_root, tax_code_map)

        case_vals = []
        level = 0
        for child in case_root.children_line_ids:
            self._get_case_child(child, level, case_vals, case_amounts)
        return case_vals

    def _vat_declaration_controls(self):
        """
        VAT declaration validation rules
        Cf. https://eservices.minfin.fgov.be/intervat
        """
        is_zero = self.currency_id.is_zero
        passed = "\u2705"
        failed = "\u26D4"

        intervat_cases = self.case_ids.filtered(
            lambda x: x.case_id.code in self._intervat_cases()
        )
        cvalues = {x.case_id.code: x.amount for x in intervat_cases}

        # blocking controls
        negative_cases = intervat_cases.filtered(lambda x: x.amount < 0.0)
        if negative_cases:
            self.note += _(
                "Negative values found for cases %s"
                % [str(x.code) for x in negative_cases]
            )
            self.note += "\n"
            self.note += _(
                "These needs to be corrected before submitting the VAT declaration."
            )
            self.note += "\n"

        # non-blocking controls
        # The text strings of the controls are modeled after the implementation
        # in Exact Online
        control = "[01] * 6% + [02] * 12% + [03] * 21% = [54]"
        c1 = cvalues["01"] * 0.06 + cvalues["02"] * 0.12 + cvalues["03"] * 0.21
        if is_zero(c1 - cvalues["54"]):
            self.controls = passed + " : " + control
        else:
            self.controls = failed + " : " + control

        control = "([84] + [86] + [88]) * 21% >= [55]"
        self.controls += "\n"
        c1 = (cvalues["84"] + cvalues["86"] + cvalues["88"]) * 0.21
        if c1 >= cvalues["55"]:
            self.controls += passed + " : " + control
        else:
            self.controls += failed + " : " + control

        control = "([85] + [87]) * 21% >= ([56] + [57])"
        self.controls += "\n"
        c1 = (cvalues["85"] + cvalues["87"]) * 0.21
        if c1 >= (cvalues["56"] + cvalues["57"]):
            self.controls += passed + " : " + control
        else:
            self.controls += failed + " : " + control

        control = "([81] + [82] + [83] + [84] + [85]) * 50% >= [59]"
        self.controls += "\n"
        c1 = (
            cvalues["81"]
            + cvalues["82"]
            + cvalues["83"]
            + cvalues["84"]
            + cvalues["85"]
        ) * 0.50
        if c1 >= cvalues["59"]:
            self.controls += passed + " : " + control
        else:
            self.controls += failed + " : " + control

        control = "[85] * 21% >= [63]"
        self.controls += "\n"
        if cvalues["85"] * 0.21 >= cvalues["63"]:
            self.controls += passed + " : " + control
        else:
            self.controls += failed + " : " + control

        control = "[49] * 21% >= [64]"
        self.controls += "\n"
        if cvalues["49"] * 0.21 >= cvalues["64"]:
            self.controls += passed + " : " + control
        else:
            self.controls += failed + " : " + control

        control = "[55] > 0 if [86] or [88] > 0"
        self.controls += "\n"
        if cvalues["86"] + cvalues["88"] and not cvalues["55"]:
            self.controls += failed + " : " + control
        else:
            self.controls += passed + " : " + control

    def _node_VATDeclaration(self, parent, ns_map, ref):

        VATDeclaration = etree.SubElement(
            parent,
            "VATDeclaration",
            attrib={"SequenceNumber": "1", "DeclarantReference": ref},
        )

        # ReplacedVATDeclaration not supported at this point in time
        # TODO:
        # Create object to save legal VAT declarations in order to
        # and add support of replacements.
        # self._node_ReplacedVATDeclaration(
        #     VATDeclaration, ns_map, replace_ref)

        self._node_Declarant(VATDeclaration, ns_map)
        self._node_Period(VATDeclaration, ns_map)

        # Deduction not supported at this point in time
        # self._node_Deduction(VATDeclaration, ns_map)

        self._node_Data(VATDeclaration, ns_map)

        ClientListingNihil = etree.SubElement(VATDeclaration, "ClientListingNihil")
        ClientListingNihil.text = self.client_nihil and "YES" or "NO"

        etree.SubElement(
            VATDeclaration,
            "Ask",
            attrib={
                "Restitution": self.ask_restitution and "YES" or "NO",
                "Payment": self.ask_payment and "YES" or "NO",
            },
        )

        # TODO: add support for attachments
        # self._node_FileAttachment(parent, ns_map)

        self._node_Comment(VATDeclaration, ns_map)

        # Justification not supported at this point in time

    def _get_grid_list(self):

        grid_list = []
        for entry in self.case_ids:
            if entry.case_id.code in self._intervat_cases():
                if self.currency_id.round(entry.amount):
                    grid_list.append(
                        {"grid": int(entry.case_id.code), "amount": entry.amount}
                    )
            elif entry.case_id.code == "VI":
                if self.currency_id.round(entry.amount) >= 0:
                    grid_list.append({"grid": 71, "amount": entry.amount})
                else:
                    grid_list.append({"grid": 72, "amount": -entry.amount})
        grid_list.sort(key=lambda k: k["grid"])
        return grid_list

    def _node_Data(self, VATDeclaration, ns_map):
        Data = etree.SubElement(VATDeclaration, "Data")

        grid_list = self._get_grid_list()

        for entry in grid_list:
            Amount = etree.SubElement(
                Data, "Amount", attrib={"GridNumber": str(entry["grid"])}
            )
            Amount.text = "%.2f" % entry["amount"]


class L10nBeVatDeclarationCase(models.TransientModel):
    _name = "l10n.be.vat.declaration.case"
    _order = "sequence"
    _description = "Periodical VAT Declaration line"

    declaration_id = fields.Many2one(
        comodel_name="l10n.be.vat.declaration", string="Periodical VAT Declaration"
    )
    case_id = fields.Many2one(comodel_name="account.tax.report.line", string="Case")
    amount = fields.Monetary(currency_field="currency_id")
    sequence = fields.Integer(related="case_id.sequence", store=True)
    level = fields.Integer()
    active = fields.Boolean()
    color = fields.Char(related="case_id.color")
    font = fields.Selection(related="case_id.font")
    currency_id = fields.Many2one(related="declaration_id.currency_id", readonly=1)

    def view_move_lines(self):
        self.ensure_one()
        act_window = self.declaration_id._move_lines_act_window()
        date_dom = self.declaration_id._get_move_line_date_domain()
        case_dom = self.declaration_id._get_case_domain(self.case_id)
        act_window["domain"] = date_dom + case_dom
        return act_window


class L10nBeVatDeclarationXlsx(models.AbstractModel):
    _name = "report.l10n_be_coa_multilang.vat_declaration_xls"
    _inherit = "report.report_xlsx.abstract"
    _description = "VAT declaration excel export"

    def _(self, src):
        lang = self.env.context.get("lang", "en_US")
        val = translate(self.env.cr, IR_TRANSLATION_NAME, "report", lang, src) or src
        return val

    def _get_ws_params(self, workbook, data, declaration):

        col_specs = {
            "case": {
                "header": {"value": self._("Case")},
                "lines": {"value": self._render("c.case_id.code")},
                "width": 8,
            },
            "name": {
                "header": {"value": self._("Description")},
                "lines": {"value": self._render("c.case_id.name")},
                "width": 70,
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
                "width": 18,
            },
        }
        wanted_list = ["case", "name", "amount"]

        return [
            {
                "ws_name": "vat_declaration_%s" % declaration.period,
                "generate_ws_method": "_generate_declaration",
                "title": declaration._description,
                "wanted_list": wanted_list,
                "col_specs": col_specs,
            }
        ]

    def _generate_declaration(self, workbook, ws, ws_params, data, declaration):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._declaration_title(ws, row_pos, ws_params, data, declaration)
        row_pos = self._declaration_info(ws, row_pos, ws_params, data, declaration)
        row_pos = self._declaration_lines(ws, row_pos, ws_params, data, declaration)

    def _declaration_title(self, ws, row_pos, ws_params, data, declaration):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _declaration_info(self, ws, row_pos, ws_params, data, declaration):
        ws.write_string(row_pos, 1, self._("Company") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, declaration.company_id.name)
        row_pos += 1
        ws.write_string(row_pos, 1, self._("VAT Number") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, declaration.company_id.vat or "")
        row_pos += 1
        ws.write_string(row_pos, 1, self._("Period") + ":", self.format_left_bold)
        ws.write_string(row_pos, 2, declaration.period)
        return row_pos + 2

    def _declaration_lines(self, ws, row_pos, ws_params, data, declaration):

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_yellow_left,
        )

        ws.freeze_panes(row_pos, 0)

        for c in declaration.case_ids:
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="lines",
                render_space={"c": c},
                default_format=self.format_tcell_left,
            )

        return row_pos + 1


class L10nBeVatDetailXlsx(models.AbstractModel):
    _name = "report.l10n_be_coa_multilang.vat_detail_xls"
    _inherit = "report.report_xlsx.abstract"
    _description = "vat declaration transactions report"

    def _(self, src):
        lang = self.env.context.get("lang", "en_US")
        val = translate(self.env.cr, IR_TRANSLATION_NAME, "report", lang, src) or src
        return val

    def _define_formats(self, wb):
        """
        Add new formats to draw a black line between Journal Entries.
        We use formats without bottom border in order to avoid
        conflicting top and bottom cell borders.
        """
        super()._define_formats(wb)

        num_format = "#,##0.00"
        date_format = "YYYY-MM-DD"

        border_grey = "#D3D3D3"
        border = {"border": True, "border_color": border_grey}
        self.format_tcell_top_grey_left = wb.add_format(dict(border, align="left"))
        self.format_tcell_top_grey_left.set_bottom(0)
        self.format_tcell_top_grey_center = wb.add_format(dict(border, align="center"))
        self.format_tcell_top_grey_center.set_bottom(0)
        self.format_tcell_top_grey_amount_right = wb.add_format(
            dict(border, num_format=num_format, align="right")
        )
        self.format_tcell_top_grey_amount_right.set_bottom(0)
        self.format_tcell_top_grey_date_left = wb.add_format(
            dict(border, num_format=date_format, align="left")
        )
        self.format_tcell_top_grey_date_left.set_bottom(0)

        border = {
            "border": True,
            "top_color": "black",
            "left_color": border_grey,
            "right_color": border_grey,
        }
        self.format_tcell_top_black_left = wb.add_format(dict(border, align="left"))
        self.format_tcell_top_black_left.set_bottom(0)
        self.format_tcell_top_black_center = wb.add_format(dict(border, align="center"))
        self.format_tcell_top_black_center.set_bottom(0)
        self.format_tcell_top_black_amount_right = wb.add_format(
            dict(border, num_format=num_format, align="right")
        )
        self.format_tcell_top_black_amount_right.set_bottom(0)
        self.format_tcell_top_black_date_left = wb.add_format(
            dict(border, num_format=date_format, align="left")
        )
        self.format_tcell_top_black_date_left.set_bottom(0)

    def _get_ws_params(self, wb, data, decl):
        dummy, self._tax_tags = decl._get_tax_code_map()
        self._date_dom = decl._get_move_line_date_domain()
        flds = ["journal_id", "debit"]
        groupby = ["journal_id"]
        totals = self.env["account.move.line"].read_group(self._date_dom, flds, groupby)
        j_dict = {}
        for entry in totals:
            if entry["debit"]:
                j_dict[entry["journal_id"][0]] = entry["debit"]
        j_ids = list(j_dict.keys())
        self._journal_totals = j_dict
        # search i.s.o. browse for account.journal _order
        # active_test = False needed to add support for the
        # inactive journals
        j_mod = self.env["account.journal"].with_context(active_test=False)
        self._journals = j_mod.search([("id", "in", j_ids)])
        slist = [self._get_centralisation_ws_params(wb, data, decl)]
        for journal in self._journals:
            slist.append(self._get_journal_ws_params(wb, data, decl, journal))
        return slist

    def _get_centralisation_ws_params(self, wb, data, decl):

        col_specs = {
            "code": {
                "header": {"value": self._("Code")},
                "lines": {"value": self._render("journal.code")},
                "width": 10,
            },
            "name": {
                "header": {"value": self._("Journal")},
                "lines": {"value": self._render("journal.name")},
                "width": 45,
            },
            "debit": {
                "header": {
                    "value": self._("Total Debit/Credit"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "type": "number",
                    "value": self._render("debit"),
                    "format": self.format_tcell_amount_right,
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("total_debit_formula"),
                    "format": self.format_theader_yellow_amount_right,
                },
                "width": 20,
            },
        }
        wl = ["code", "name", "debit"]

        title = (10 * " ").join(
            [decl.company_id.name, _("Journal Centralisation"), decl.period]
        )

        return {
            "ws_name": self._("Centralisation"),
            "generate_ws_method": "_centralisation_report",
            "title": title,
            "wanted_list": wl,
            "col_specs": col_specs,
        }

    def _centralisation_report(self, wb, ws, ws_params, data, decl):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._centralisation_title(ws, row_pos, ws_params, data, decl)
        row_pos = self._centralisation_lines(ws, row_pos, ws_params, data, decl)

    def _centralisation_title(self, ws, row_pos, ws_params, data, decl):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _centralisation_lines(self, ws, row_pos, ws_params, data, decl):

        wl = ws_params["wanted_list"]
        debit_pos = wl.index("debit")
        start_pos = row_pos + 1

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_yellow_left,
        )

        ws.freeze_panes(row_pos, 0)

        for journal in self._journals:
            debit = self._journal_totals[journal.id]
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="lines",
                render_space={"journal": journal, "debit": debit},
                default_format=self.format_tcell_left,
            )

        debit_start = self._rowcol_to_cell(start_pos, debit_pos)
        debit_stop = self._rowcol_to_cell(row_pos - 1, debit_pos)
        total_debit_formula = "SUM({}:{})".format(debit_start, debit_stop)
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={"total_debit_formula": total_debit_formula},
            default_format=self.format_theader_yellow_left,
        )

        return row_pos + 1

    def _get_journal_template(self):
        template = {
            "move_name": {
                "header": {"value": self._("Entry")},
                "lines": {
                    "value": self._render(
                        "l.move_id.name != '/' and l.move_id.name "
                        "or ('*' + str(l.move_id))"
                    )
                },
                "width": 20,
            },
            "move_date": {
                "header": {"value": self._("Effective Date")},
                "lines": {
                    "value": self._render(
                        "datetime.combine(l.date, datetime.min.time())"
                    ),
                    "format": self._render("format_tcell_date_left"),
                },
                "width": 13,
            },
            "acc_code": {
                "header": {"value": self._("Account")},
                "lines": {"value": self._render("l.account_id.code")},
                "width": 12,
            },
            "acc_name": {
                "header": {"value": self._("Account Name")},
                "lines": {"value": self._render("l.account_id.name")},
                "width": 36,
            },
            "aml_name": {
                "header": {"value": self._("Name")},
                "lines": {"value": self._render("l.name")},
                "width": 42,
            },
            "journal_code": {
                "header": {"value": self._("Journal")},
                "lines": {"value": self._render("l.journal_id.code")},
                "width": 10,
            },
            "journal": {
                "header": {"value": self._("Journal")},
                "lines": {"value": self._render("l.journal_id.name")},
                "width": 20,
            },
            "analytic_account_name": {
                "header": {"value": self._("Analytic Account")},
                "lines": {
                    "value": self._render(
                        "l.analytic_account_id and l.analytic_account_id.name"
                    )
                },
                "width": 20,
            },
            "analytic_account_code": {
                "header": {"value": self._("Analytic Account Reference")},
                "lines": {
                    "value": self._render(
                        "l.analytic_account_id and l.analytic_account_id.code or ''"
                    )
                },
                "width": 20,
            },
            "partner_name": {
                "header": {"value": self._("Partner")},
                "lines": {"value": self._render("l.partner_id and l.partner_id.name")},
                "width": 36,
            },
            "partner_ref": {
                "header": {"value": self._("Partner Reference")},
                "lines": {
                    "value": self._render("l.partner_id and l.partner_id.ref or ''")
                },
                "width": 10,
            },
            "date_maturity": {
                "header": {"value": self._("Maturity Date")},
                "lines": {
                    "value": self._render(
                        "datetime.combine(l._maturity, datetime.min.time())"
                    ),
                    "format": self._render("format_tcell_date_left"),
                },
                "width": 13,
            },
            "debit": {
                "header": {
                    "value": self._("Debit"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("l.debit"),
                    "format": self._render("format_tcell_amount_right"),
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("debit_formula"),
                    "format": self.format_theader_yellow_amount_right,
                },
                "width": 18,
            },
            "credit": {
                "header": {
                    "value": self._("Credit"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("l.credit"),
                    "format": self._render("format_tcell_amount_right"),
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("credit_formula"),
                    "format": self.format_theader_yellow_amount_right,
                },
                "width": 18,
            },
            "balance": {
                "header": {
                    "value": self._("Balance"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("l.balance"),
                    "format": self._render("format_tcell_amount_right"),
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("bal_formula"),
                    "format": self.format_theader_yellow_amount_right,
                },
                "width": 18,
            },
            "full_reconcile": {
                "header": {
                    "value": self._("Rec."),
                    "format": self.format_theader_yellow_center,
                },
                "lines": {
                    "value": self._render(
                        "l.full_reconcile_id and l.full_reconcile_id.name"
                    ),
                    "format": self._render("format_tcell_center"),
                },
                "width": 12,
            },
            "reconcile_amount": {
                "header": {"value": self._("Reconcile Amount")},
                "lines": {
                    "value": self._render(
                        "l.full_reconcile_id and l.balance or "
                        "(sum(l.matched_credit_ids.mapped('amount')) - "
                        "sum(l.matched_debit_ids.mapped('amount')))"
                    ),
                    "format": self._render("format_tcell_amount_right"),
                },
                "width": 12,
            },
            "tax_code": {
                "header": {
                    "value": self._("VAT"),
                    "format": self.format_theader_yellow_center,
                },
                "lines": {
                    "value": self._render("tax_code"),
                    "format": self._render("format_tcell_center"),
                },
                "width": 10,
            },
            "tax_amount": {
                "header": {"value": self._("VAT Amount")},
                "lines": {
                    "value": self._render("tax_amount"),
                    "format": self._render("format_tcell_amount_right"),
                },
                "width": 18,
            },
            "amount_currency": {
                "header": {
                    "value": self._("Am. Currency"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("l.amount_currency"),
                    "format": self._render("format_tcell_amount_right"),
                },
                "width": 18,
            },
            "currency_name": {
                "header": {
                    "value": self._("Curr."),
                    "format": self.format_theader_yellow_center,
                },
                "lines": {
                    "value": self._render("l.currency_id and l.currency_id.name"),
                    "format": self._render("format_tcell_center"),
                },
                "width": 6,
            },
            "move_ref": {
                "header": {"value": self._("Entry Reference")},
                "lines": {"value": self._render("l.move_id.name")},
                "width": 25,
            },
            "move_id": {
                "header": {"value": self._("Entry Ide")},
                "lines": {"value": self._render("str(l.move_id.id)")},
                "width": 10,
            },
        }
        return template

    def _get_vat_summary_template(self):
        """
        XLS Template VAT Summary
        """
        template = {
            "tax_code": {
                "header": {"value": self._("Case")},
                "lines": {"value": self._render("tc")},
                "width": 6,
            },
            "tax_amount": {
                "header": {
                    "value": self._("Amount"),
                    "format": self.format_theader_yellow_right,
                },
                "lines": {
                    "value": self._render("tax_totals[tc]"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
        }
        return template

    def _get_journal_ws_params(self, wb, data, decl, journal):
        col_specs = self._get_journal_template()
        col_specs.update(self.env["account.journal"]._report_xlsx_template())
        wl = self.env["account.journal"]._report_xlsx_fields()
        title = (10 * " ").join(
            [
                decl.company_id.name,
                journal.name + "({})".format(journal.code),
                decl.period,
            ]
        )
        ws_params_summary = {
            "col_specs": self._get_vat_summary_template(),
            "wanted_list": ["tax_code", "tax_amount"],
        }
        return {
            "ws_name": journal.code,
            "generate_ws_method": "_journal_report",
            "title": title,
            "wanted_list": wl,
            "col_specs": col_specs,
            "ws_params_summary": ws_params_summary,
            "journal": journal,
        }

    def _journal_report(self, wb, ws, ws_params, data, decl):

        time_start = time.time()
        ws.set_landscape()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        journal = ws_params["journal"]
        row_pos = self._journal_title(ws, row_pos, ws_params, data, decl, journal)
        row_pos = self._journal_lines(ws, row_pos, ws_params, data, decl, journal)
        time_end = time.time() - time_start
        _logger.debug(
            "VAT Transaction report processing time for Journal %s = %.3f seconds",
            journal.code,
            time_end,
        )

    def _journal_title(self, ws, row_pos, ws_params, data, decl, journal):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _journal_lines(self, ws, row_pos, ws_params, data, decl, journal):

        wl = ws_params["wanted_list"]
        debit_pos = wl.index("debit")
        credit_pos = wl.index("credit")
        start_pos = row_pos + 1

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_yellow_left,
        )

        ws.freeze_panes(row_pos, 0)

        am_dom = self._date_dom + [("journal_id", "=", journal.id)]
        ams = self.env["account.move"].search(am_dom, order="name, date")
        amls = ams.mapped("line_ids")

        tax_totals = {}
        cround = decl.company_id.currency_id.round
        am = self.env["account.move"]
        new_am = False
        am_cnt = 0
        for aml in amls:
            if aml.move_id != am:
                am = aml.move_id
                new_am = True
                am_cnt += 1
            else:
                new_am = False
            tax_codes = []
            tax_amount = None
            for tag in aml.tag_ids:
                if tag not in self._tax_tags:
                    continue
                tc = tc_str = tag.name[1:]
                sign = tag.tax_negate and 1 or -1
                tax_amount = cround(sign * aml.balance)
                if tax_amount < 0:
                    tc_str += "(-1)"
                if tc_str not in tax_codes:
                    tax_codes.append(tc_str)
                    if tc not in tax_totals:
                        tax_totals[tc] = tax_amount
                    else:
                        tax_totals[tc] += tax_amount

            if new_am and am_cnt > 1:
                default_format = self.format_tcell_top_black_left
                format_tcell_center = self.format_tcell_top_black_center
                format_tcell_amount_right = self.format_tcell_top_black_amount_right
                format_tcell_date_left = self.format_tcell_top_black_date_left
            else:
                default_format = self.format_tcell_top_grey_left
                format_tcell_center = self.format_tcell_top_grey_center
                format_tcell_amount_right = self.format_tcell_top_grey_amount_right
                format_tcell_date_left = self.format_tcell_top_grey_date_left
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="lines",
                render_space={
                    "l": aml,
                    "tax_code": ", ".join(tax_codes),
                    "tax_amount": tax_amount and abs(tax_amount),
                    "format_tcell_center": format_tcell_center,
                    "format_tcell_amount_right": format_tcell_amount_right,
                    "format_tcell_date_left": format_tcell_date_left,
                },
                default_format=default_format,
            )

        debit_start = self._rowcol_to_cell(start_pos, debit_pos)
        debit_stop = self._rowcol_to_cell(row_pos - 1, debit_pos)
        debit_formula = "SUM({}:{})".format(debit_start, debit_stop)
        credit_start = self._rowcol_to_cell(start_pos, credit_pos)
        credit_stop = self._rowcol_to_cell(row_pos - 1, credit_pos)
        credit_formula = "SUM({}:{})".format(credit_start, credit_stop)
        debit_cell = self._rowcol_to_cell(row_pos, debit_pos)
        credit_cell = self._rowcol_to_cell(row_pos, credit_pos)
        bal_formula = debit_cell + "-" + credit_cell

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={
                "debit_formula": debit_formula,
                "credit_formula": credit_formula,
                "bal_formula": bal_formula,
            },
            default_format=self.format_theader_yellow_left,
        )

        ws_params_summary = ws_params["ws_params_summary"]
        row_pos += 1
        tcs = list(tax_totals.keys())
        tcs.sort()
        if tcs:
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params_summary,
                col_specs_section="header",
                default_format=self.format_theader_yellow_left,
            )
            for tc in tcs:
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params_summary,
                    col_specs_section="lines",
                    render_space={"l": aml, "tc": tc, "tax_totals": tax_totals},
                    default_format=self.format_tcell_left,
                )

        return row_pos + 1
