# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import io
import json
import logging
import os
import time
from datetime import datetime

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMoveLineImport(models.TransientModel):
    _name = "aml.import"
    _description = "Import account move lines"

    aml_data = fields.Binary(string="File", required=True)
    aml_fname = fields.Char(string="Filename")
    file_type = fields.Selection(
        selection=[("csv", "csv"), ("xls", "xls"), ("xlsx", "xlsx")]
    )
    sheet = fields.Char(
        help="Specify the Excel sheet."
        "\nIf not specified the first sheet will be retrieved."
    )
    dialect = fields.Char(help="JSON dictionary to store the csv dialect")
    csv_separator = fields.Selection(
        selection=[(",", ", (comma)"), (";", "; (semicolon)")], string="CSV Separator"
    )
    decimal_separator = fields.Selection(
        selection=[(".", ". (dot)"), (",", ", (comma)")],
        string="Decimal Separator",
        default=".",
    )
    codepage = fields.Char(
        string="Code Page",
        help="Code Page of the system that has generated the csv file."
        "\nE.g. Windows-1252, utf-8",
    )
    warning = fields.Text(readonly=True)
    note = fields.Text("Log")

    @api.onchange("aml_fname")
    def _onchange_aml_fname(self):
        if not self.aml_fname:
            return
        name, ext = os.path.splitext(self.aml_fname)
        ext = ext[1:]
        if ext not in ["csv", "xls", "xlsx"]:
            self.warning = _(
                "<b>Incorrect file format !</b>"
                "<br>Only files of type csv and xls(x) are supported."
            )
            return
        else:
            self.file_type = ext
            self.warning = False
        if ext == "csv":
            self.codepage = self._default_csv_codepage()
        else:
            self.codepage = self._default_xls_codepage()

    def _default_csv_codepage(self):
        return "utf-8"

    def _default_xls_codepage(self):
        return "utf-16le"

    @api.onchange("sheet")
    def _onchange_sheet(self):
        self.warning = False

    @api.onchange("aml_data")
    def _onchange_aml_data(self):
        if self.file_type == "csv" and self.aml_data:
            self._guess_dialect()

    def _guess_dialect(self):
        # the self.aml_data is type 'str' during the onchange processing,
        # hence we convert into bytes so that we can try to determine the
        # csv dialect
        lines = bytes(self.aml_data, encoding=self.codepage)
        lines = base64.decodestring(lines)
        # convert windows & mac line endings to unix style
        lines = lines.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        first_lines = lines.split(b"\n", 3)
        try:
            sample = b"\n".join(first_lines[:3]).decode(self.codepage)
            dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        except Exception:
            dialect = csv.Sniffer().sniff('"header 1";"header 2";\n')
            if b";" in first_lines[0]:
                dialect.delimiter = ";"
            elif b"," in first_lines[0]:
                dialect.delimiter = ","
        self.csv_separator = dialect.delimiter
        dialect.lineterminator = "\n"
        if self.csv_separator == ";":
            self.decimal_separator = ","
        if lines[:3] == b"\xef\xbb\xbf":
            self.codepage = "utf-8-sig"
        dialect_dict = dialect2dict(dialect)
        self.dialect = json.dumps(dialect_dict)

    @api.onchange("csv_separator")
    def _onchange_csv_separator(self):
        if self.csv_separator and self.aml_data:
            dialect_dict = json.loads(self.dialect)
            if dialect_dict["delimiter"] != self.csv_separator:
                dialect_dict["delimiter"] = self.csv_separator
                self.dialect = json.dumps(dialect_dict)

    def _read_csv(self, data):
        # convert windows & mac line endings to unix style
        lines = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        lines, header = self._remove_leading_lines(lines.decode(self.codepage))
        dialect_dict = json.loads(self.dialect)
        header_fields = next(csv.reader(io.StringIO(header), **dialect_dict))
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(
            io.StringIO(lines), fieldnames=self._header_fields, **dialect_dict
        )
        return reader

    def _read_xls(self, data):  # noqa: C901
        wb = xlrd.open_workbook(file_contents=data)
        if self.sheet:
            try:
                sheet = wb.sheet_by_name(self.sheet)
            except xlrd.XLRDError as e:
                self.warning = _(
                    "Error while reading Excel sheet: <br>{}".format(str(e))
                )
                return
        else:
            sheet = wb.sheet_by_index(0)
        lines = []
        header = False
        for ri in range(sheet.nrows):
            err_msg = ""
            line = {}
            ln = sheet.row_values(ri)
            if not ln or ln and ln[0] == "#":
                continue
            if not header:
                header = [x.lower() for x in ln]
                self._header_fields = self._process_header(header)
            else:
                for ci, hf in enumerate(self._header_fields):
                    line[hf] = False
                    val = False
                    cell = sheet.cell(ri, ci)
                    if hf in self._skip_fields:
                        continue
                    if cell.ctype in [xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK]:
                        continue
                    if cell.ctype == xlrd.XL_CELL_ERROR:
                        if err_msg:
                            err_msg += "\n"
                        err_msg += _("Incorrect value '%s' " "for field '%s' !") % (
                            cell.value,
                            hf,
                        )
                        continue

                    fmt = self._field_methods[hf]["field_type"]

                    if fmt == "char":
                        if cell.ctype == xlrd.XL_CELL_TEXT:
                            val = cell.value
                        elif cell.ctype == xlrd.XL_CELL_NUMBER:
                            is_int = cell.value % 1 == 0.0
                            if is_int:
                                val = str(int(cell.value))
                            else:
                                val = str(cell.value)
                        else:
                            val = str(cell.value)

                    elif fmt == "float":
                        if cell.ctype == xlrd.XL_CELL_TEXT:
                            amount = cell.value
                            decimal_separator = "."
                            dot_i = amount.rfind(".")
                            comma_i = amount.rfind(",")
                            if comma_i > dot_i and comma_i > 0:
                                decimal_separator = ","
                            val = str2float(amount, decimal_separator)
                        else:
                            val = cell.value

                    elif fmt in ["integer", "many2one"]:
                        val = cell.value
                        if val:
                            is_int = val % 1 == 0.0
                            if is_int:
                                val = int(val)
                            else:
                                if err_msg:
                                    err_msg += "\n"
                                err_msg += _(
                                    "Incorrect value '%s' "
                                    "for field '%s' of type %s !"
                                ) % (cell.value, hf, fmt.capitalize())

                    elif fmt == "boolean":
                        if cell.ctype == xlrd.XL_CELL_TEXT:
                            val = cell.value.capitalize().strip()
                            if val in ["", "0", "False"]:
                                val = False
                            elif val in ["1", "True"]:
                                val = True
                        else:
                            is_int = cell.value % 1 == 0.0
                            if is_int:
                                val = 1 and True or False
                            else:
                                val = None
                        if val is None:
                            if err_msg:
                                err_msg += "\n"
                            err_msg += _(
                                "Incorrect value '%s' "
                                "for field '%s' of type Boolean !"
                            ) % (cell.value, hf)

                    elif fmt == "date":
                        if cell.ctype == xlrd.XL_CELL_TEXT:
                            if cell.value:
                                val = str2date(cell.value)
                                if not val:
                                    if err_msg:
                                        err_msg += "\n"
                                    err_msg += _(
                                        "Incorrect value '%s' "
                                        "for field '%s' of type Date !"
                                        " should be YYYY-MM-DD"
                                    ) % (cell.value, hf)
                        elif cell.ctype in [xlrd.XL_CELL_NUMBER, xlrd.XL_CELL_DATE]:
                            val = xlrd.xldate.xldate_as_tuple(cell.value, wb.datemode)
                            val = datetime(*val).strftime("%Y-%m-%d")
                        elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                            if err_msg:
                                err_msg += "\n"
                            err_msg += _(
                                "Incorrect value '%s' " "for field '%s' of type Date !"
                            ) % (cell.value, hf)

                    else:
                        _logger.error(
                            "%s, field '%s', Unsupported format '%s'",
                            self._name,
                            hf,
                            fmt,
                        )
                        raise NotImplementedError

                    if val:
                        line[hf] = val

                if err_msg:
                    self._log_line_error(line, err_msg)

                if line:
                    lines.append(line)

        return lines

    def aml_import(self):
        time_start = time.time()
        self._err_log = ""
        move = self.env["account.move"].browse(self._context["active_id"])
        accounts = self.env["account.account"].search(
            [("deprecated", "=", False), ("company_id", "=", move.company_id.id)]
        )
        self._accounts_dict = {a.code: a.id for a in accounts}
        self._sum_debit = self._sum_credit = 0.0
        self._get_orm_fields()
        data = base64.decodestring(self.aml_data)
        if self.file_type == "csv":
            lines = self._read_csv(data)
        elif self.file_type in ["xls", "xlsx"]:
            lines = self._read_xls(data)
        else:
            raise NotImplementedError
        if self.warning:
            module = __name__.split("addons.")[1].split(".")[0]
            view = self.env.ref("%s.aml_import_view_form" % module)
            return {
                "name": _("Import File"),
                "res_id": self.id,
                "view_type": "form",
                "view_mode": "form",
                "res_model": "aml.import",
                "view_id": view.id,
                "target": "new",
                "type": "ir.actions.act_window",
                "context": self.env.context,
            }

        move_lines = []
        for line in lines:

            aml_vals = {}

            # process input fields
            for i, hf in enumerate(self._header_fields):
                if i == 0 and line[hf] and line[hf][0] == "#":
                    # lines starting with # are considered as comment lines
                    break
                if hf in self._skip_fields:
                    continue
                if line[hf] in ["", False]:
                    continue

                if self._field_methods[hf].get("orm_field"):
                    self._field_methods[hf]["method"](
                        hf,
                        line,
                        move,
                        aml_vals,
                        orm_field=self._field_methods[hf]["orm_field"],
                    )
                else:
                    self._field_methods[hf]["method"](hf, line, move, aml_vals)

            if aml_vals:
                self._process_line_vals(line, move, aml_vals)
                move_lines.append(aml_vals)

        vals = [(0, 0, r) for r in move_lines]
        vals = self._process_vals(move, vals)

        if self._err_log:
            self.note = self._err_log
            module = __name__.split("addons.")[1].split(".")[0]
            result_view = self.env.ref("%s.aml_import_view_form_result" % module)
            return {
                "name": _("Import File result"),
                "res_id": self.id,
                "view_type": "form",
                "view_mode": "form",
                "res_model": "aml.import",
                "view_id": result_view.id,
                "target": "new",
                "type": "ir.actions.act_window",
            }
        else:
            ctx = dict(self._context, check_move_validity=True)
            move.with_context(ctx).write({"line_ids": vals})
            import_time = time.time() - time_start
            _logger.warn(
                "account.move %s import time = %.3f seconds", move.name, import_time
            )
            return {"type": "ir.actions.act_window_close"}

    def _remove_leading_lines(self, lines):
        """ remove leading blank or comment lines """
        input_buffer = io.StringIO(lines)
        header = False
        while not header:
            ln = next(input_buffer)
            if not ln or ln and ln[0] in [self.csv_separator, "#"]:
                continue
            else:
                header = ln.lower()
        if not header:
            raise UserError(_("No header line found in the input file !"))
        output = input_buffer.read()
        return output, header

    def _input_fields(self):
        """
        Extend this dictionary if you want to add support for
        fields requiring pre-processing before being added to
        the move line values dict.

        TODO: add support for taxes.
        """
        res = {
            "account": {"method": self._handle_account, "field_type": "char"},
            "account_id": {"required": True},
            "debit": {"method": self._handle_debit, "field_type": "float"},
            "credit": {"method": self._handle_credit, "field_type": "float"},
            "partner": {"method": self._handle_partner, "field_type": "char"},
            "product": {"method": self._handle_product, "field_type": "char"},
            "date_maturity": {
                "method": self._handle_date_maturity,
                "field_type": "date",
            },
            "due date": {"method": self._handle_date_maturity, "field_type": "date"},
            "currency": {"method": self._handle_currency, "field_type": "char"},
            "analytic account": {
                "method": self._handle_analytic_account,
                "field_type": "char",
            },
        }
        return res

    def _get_orm_fields(self):
        aml_mod = self.env["account.move.line"]
        orm_fields = aml_mod.fields_get()
        blacklist = models.MAGIC_COLUMNS + [aml_mod.CONCURRENCY_CHECK_FIELD]
        self._orm_fields = {
            f: orm_fields[f]
            for f in orm_fields
            if f not in blacklist and not orm_fields[f].get("depends")
        }

    def _process_header(self, header_fields):

        self._field_methods = self._input_fields()
        self._skip_fields = []

        # header fields after blank column are considered as comments
        column_cnt = 0
        for cnt in range(len(header_fields)):
            if header_fields[cnt] == "":
                column_cnt = cnt
                break
            elif cnt == len(header_fields) - 1:
                column_cnt = cnt + 1
                break
        header_fields = header_fields[:column_cnt]

        # check for duplicate header fields
        header_fields2 = []
        for hf in header_fields:
            if hf in header_fields2:
                raise UserError(
                    _(
                        "Duplicate header field '%s' found !"
                        "\nPlease correct the input file."
                    )
                    % hf
                )
            else:
                header_fields2.append(hf)

        for hf in header_fields:

            if hf in self._field_methods and self._field_methods[hf].get("method"):
                if not self._field_methods[hf].get("field_type"):
                    raise UserError(
                        _(
                            "Programming Error:"
                            "\nMissing formatting info for column '%s'." % hf
                        )
                    )
                continue

            if hf not in self._orm_fields and hf not in [
                self._orm_fields[f]["string"].lower() for f in self._orm_fields
            ]:
                _logger.error(
                    _("%s, undefined field '%s' found " "while importing move lines"),
                    self._name,
                    hf,
                )
                self._skip_fields.append(hf)
                continue

            field_def = self._orm_fields.get(hf)
            if not field_def:
                for f in self._orm_fields:
                    if self._orm_fields[f]["string"].lower() == hf:
                        orm_field = f
                        field_def = self._orm_fields.get(f)
                        break
            else:
                orm_field = hf
            field_type = field_def["type"]

            try:
                ft = field_type == "text" and "char" or field_type
                self._field_methods[hf] = {
                    "method": getattr(self, "_handle_orm_%s" % ft),
                    "orm_field": orm_field,
                    "field_type": field_type,
                }
            except AttributeError:
                _logger.error(
                    _(
                        "%s, field '%s', "
                        "the import of ORM fields of type '%s' "
                        "is not supported"
                    ),
                    self._name,
                    hf,
                    field_type,
                )
                self._skip_fields.append(hf)

        return header_fields

    def _log_line_error(self, line, msg):
        if not line.get("log_line_error"):
            data = " | ".join(["%s" % line[hf] for hf in self._header_fields])
            self._err_log += (
                _("Error when processing line '%s'") % data + ":\n" + msg + "\n\n"
            )
            # Add flag to avoid reporting two times the same line.
            # This could happen for errors detected by
            # _read_xls as well as _proces_%
            line["log_line_error"] = True

    def _handle_orm_char(self, field, line, move, aml_vals, orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            aml_vals[orm_field] = line[field]

    def _handle_orm_integer(self, field, line, move, aml_vals, orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = line[field]
            if val:
                if isinstance(val, str):
                    val = str2int(val.strip(), self.decimal_separator)
                elif isinstance(val, (float, bool)):
                    is_int = val % 1 == 0.0
                    if is_int:
                        val = int(val)
                    else:
                        val = False
                if val is False:
                    msg = _(
                        "Incorrect value '%s' " "for field '%s' of type Integer !"
                    ) % (line[field], field)
                    self._log_line_error(line, msg)
                else:
                    aml_vals[orm_field] = val

    def _handle_orm_float(self, field, line, move, aml_vals, orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = line[field]
            if val:
                if isinstance(val, str):
                    val = val.strip()
                elif isinstance(val, (float, bool)):
                    is_int = val % 1 == 0.0
                    if is_int:
                        val = int(val)
                    else:
                        val = False
                if val is False:
                    val = str2float(line[field], self.decimal_separator)
                    if val is False:
                        msg = _(
                            "Incorrect value '%s' " "for field '%s' of type Numeric !"
                        ) % (line[field], field)
                        self._log_line_error(line, msg)
                else:
                    aml_vals[orm_field] = val

    def _handle_orm_boolean(self, field, line, move, aml_vals, orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = line[field]
            if isinstance(val, str):
                val = val.strip().capitalize()
                if val in ["", "0", "False"]:
                    val = False
                elif val in ["1", "True"]:
                    val = True
                if isinstance(val, str):
                    msg = _(
                        "Incorrect value '%s' " "for field '%s' of type Boolean !"
                    ) % (line[field], field)
                    self._log_line_error(line, msg)
            aml_vals[orm_field] = val

    def _handle_orm_many2one(self, field, line, move, aml_vals, orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = line[field]
            if val:
                if isinstance(val, str):
                    val = str2int(val.strip(), self.decimal_separator)
                elif isinstance(val, (float, bool)):
                    is_int = val % 1 == 0.0
                    if is_int:
                        val = int(val)
                    else:
                        val = False
                if val is False:
                    msg = _(
                        "Incorrect value '%s' " "for field '%s' of type Many2one !"
                    ) % (line[field], field)
                    self._log_line_error(line, msg)
                else:
                    aml_vals[orm_field] = val

    def _handle_account(self, field, line, move, aml_vals):
        if not aml_vals.get("account_id"):
            code = line[field]
            if code in self._accounts_dict:
                aml_vals["account_id"] = self._accounts_dict[code]
            else:
                msg = _("Account with code '%s' not found !") % code
                self._log_line_error(line, msg)

    def _handle_debit(self, field, line, move, aml_vals):
        if "debit" not in aml_vals:
            debit = line[field]
            if isinstance(debit, str):
                debit = str2float(debit, self.decimal_separator)
            aml_vals["debit"] = debit
            self._sum_debit += debit

    def _handle_credit(self, field, line, move, aml_vals):
        if "credit" not in aml_vals:
            credit = line[field]
            if isinstance(credit, str):
                credit = str2float(credit, self.decimal_separator)
            aml_vals["credit"] = credit
            self._sum_credit += credit

    def _handle_partner(self, field, line, move, aml_vals):
        if not aml_vals.get("partner_id"):
            input_val = line[field]
            part_mod = self.env["res.partner"]
            dom = ["|", ("parent_id", "=", False), ("is_company", "=", True)]
            dom_ref = dom + [("ref", "=", input_val)]
            partners = part_mod.search(dom_ref)
            if not partners:
                dom_name = dom + [("name", "=", input_val)]
                partners = part_mod.search(dom_name)
            if not partners:
                msg = _("Partner '%s' not found !") % input_val
                self._log_line_error(line, msg)
                return
            elif len(partners) > 1:
                msg = (
                    _("Multiple partners with Reference " "or Name '%s' found !")
                    % input_val
                )
                self._log_line_error(line, msg)
                return
            else:
                partner = partners[0]
                aml_vals["partner_id"] = partner.id

    def _handle_product(self, field, line, move, aml_vals):
        if not aml_vals.get("product_id"):
            input_val = line[field]
            prod_mod = self.env["product.product"]
            products = prod_mod.search([("default_code", "=", input_val)])
            if not products:
                products = prod_mod.search([("name", "=", input_val)])
            if not products:
                msg = _("Product '%s' not found !") % input_val
                self._log_line_error(line, msg)
                return
            elif len(products) > 1:
                msg = (
                    _(
                        "Multiple products with Internal Reference "
                        "or Name '%s' found !"
                    )
                    % input_val
                )
                self._log_line_error(line, msg)
                return
            else:
                product = products[0]
                aml_vals["product_id"] = product.id

    def _handle_date_maturity(self, field, line, move, aml_vals):
        if not aml_vals.get("date_maturity"):
            due = line[field]
            try:
                datetime.strptime(due, "%Y-%m-%d")
                aml_vals["date_maturity"] = due
            except Exception:
                msg = _(
                    "Incorrect data format for field '%s' "
                    "with value '%s', "
                    " should be YYYY-MM-DD"
                ) % (field, due)
                self._log_line_error(line, msg)

    def _handle_currency(self, field, line, move, aml_vals):
        if not aml_vals.get("currency_id"):
            name = line[field]
            curr = self.env["res.currency"].search([("name", "=ilike", name)])
            if curr:
                aml_vals["currency_id"] = curr[0].id
            else:
                msg = _("Currency '%s' not found !") % name
                self._log_line_error(line, msg)

    def _handle_analytic_account(self, field, line, move, aml_vals):
        if not aml_vals.get("analytic_account_id"):
            ana_mod = self.env["account.analytic.account"]
            input_val = line[field]
            domain = [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", move.company_id.id),
            ]
            analytic_accounts = ana_mod.search(domain + [("code", "=", input_val)])
            if len(analytic_accounts) == 1:
                aml_vals["analytic_account_id"] = analytic_accounts.id
            else:
                analytic_accounts = ana_mod.search(domain + [("name", "=", input_val)])
                if len(analytic_accounts) == 1:
                    aml_vals["analytic_account_id"] = analytic_accounts.id
            if not analytic_accounts:
                msg = _("Invalid Analytic Account '%s' !") % input_val
                self._log_line_error(line, msg)
            elif len(analytic_accounts) > 1:
                msg = (
                    _("Multiple Analytic Accounts found " "that match with '%s' !")
                    % input
                )
                self._log_line_error(line, msg)

    def _process_line_vals(self, line, move, aml_vals):
        """
        Use this method if you want to check/modify the
        line input values dict before calling the move write() method
        """
        self._process_line_vals_currency(line, move, aml_vals)

        if "name" not in aml_vals:
            aml_vals["name"] = "/"

        if "debit" not in aml_vals:
            aml_vals["debit"] = 0.0

        if "credit" not in aml_vals:
            aml_vals["credit"] = 0.0

        if (
            aml_vals["debit"] < 0
            or aml_vals["credit"] < 0
            or aml_vals["debit"] * aml_vals["credit"] != 0
        ):
            msg = _("Incorrect debit/credit values !")
            self._log_line_error(line, msg)

        if "partner_id" not in aml_vals:
            # required since otherwise the partner_id
            # of the previous entry is added
            aml_vals["partner_id"] = False

        all_fields = self._field_methods
        required_fields = [x for x in all_fields if all_fields[x].get("required")]
        for rf in required_fields:
            if rf not in aml_vals:
                msg = (
                    _(
                        "The '%s' field is a required field "
                        "that must be correctly set."
                    )
                    % rf
                )
                self._log_line_error(line, msg)

    def _process_line_vals_currency(self, line, move, aml_vals):
        if "currency_id" in aml_vals:
            amt_cur = aml_vals.get("amount_currency", 0.0)
            debit = aml_vals.get("debit", 0.0)
            credit = aml_vals.get("credit", 0.0)
            ctx = {"date": move.date}
            cur = (
                self.env["res.currency"]
                .with_context(ctx)
                .browse(aml_vals["currency_id"])
            )
            comp_cur = move.company_id.currency_id.with_context(ctx)

            if (debit or credit) and not amt_cur:
                amt = debit or -credit
                aml_vals["amount_currency"] = comp_cur.compute(amt, cur)

            elif amt_cur and not (debit or credit):
                amt = cur.compute(amt_cur, comp_cur)
                if amt > 0:
                    aml_vals["debit"] = amt
                else:
                    aml_vals["credit"] = -amt

    def _process_vals(self, move, vals):
        """
        Use this method if you want to check/modify the
        input values dict before calling the move write() method
        """
        dp = self.env["decimal.precision"].precision_get("Account")
        if round(self._sum_debit, dp) != round(self._sum_credit, dp):
            self._err_log += (
                "\n"
                + _(
                    "Error in input file, Total Debit (%s) is "
                    "different from Total Credit (%s) !"
                )
                % (self._sum_debit, self._sum_credit)
                + "\n"
            )
        return vals


def dialect2dict(dialect):
    attrs = [
        "delimiter",
        "doublequote",
        "escapechar",
        "lineterminator",
        "quotechar",
        "quoting",
        "skipinitialspace",
    ]
    return {k: getattr(dialect, k) for k in attrs}


def str2float(amount, decimal_separator):
    if not amount:
        return 0.0
    try:
        if decimal_separator == ".":
            return float(amount.replace(",", ""))
        else:
            return float(amount.replace(".", "").replace(",", "."))
    except Exception:
        return False


def str2int(amount, decimal_separator):
    if not amount:
        return 0
    try:
        if decimal_separator == ".":
            return int(amount.replace(",", ""))
        else:
            return int(amount.replace(".", "").replace(",", "."))
    except Exception:
        return False


def str2date(date_str):
    try:
        return time.strftime("%Y-%m-%d", time.strptime(date_str, "%Y-%m-%d"))
    except Exception:
        return False
