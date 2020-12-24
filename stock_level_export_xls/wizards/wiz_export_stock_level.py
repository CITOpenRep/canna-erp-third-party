# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class WizExportStockLevel(models.TransientModel):
    _name = "wiz.export.stock.level"
    _description = "Generate a stock level report for a given date"

    stock_level_date = fields.Datetime(
        string="Stock Level Date",
        help="Specify the Date & Time for the Stock Levels."
        "\nThe current stock level will be given if not specified.",
    )
    categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        help="Limit the export to the selected Product Category.",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        help="Limit the export to the selected Product.",
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
        help="Limit the export to the selected Lot.",
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        help="Limit the export to the selected Warehouse.",
    )
    location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations",
        domain=[("usage", "=", "internal")],
        help="Limit the export to the selected Locations.",
    )
    owner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        help="Limit the export to the selected stock owner.",
    )
    package_id = fields.Many2one(comodel_name="stock.quant.package", string="Package")
    # product_type limited to base.group_no_one since consumables
    # are not supposed to be used for stock management purposes
    product_type = fields.Selection(
        selection=[("product", "Storable Product"), ("consu", "Consumable")],
        string="Product Type",
        default="product",
        help="Leave blank to include Stockable and Consumable products",
    )
    product_select = fields.Selection(
        selection=[("all", "All Products"), ("select", "Selected Products")],
        string="Products",
        default=lambda self: self._default_product_select(),
    )
    import_compatible = fields.Boolean(
        string="Import Compatible Export",
        help="Generate a file for use with the 'stock_level_import' module.",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        domain=[("usage", "=", "internal")],
        help="Limit the export to the selected Location.",
    )
    add_cost = fields.Boolean(
        string="Add cost",
        help="Product cost at Stock Level Date."
        "\nThe resulting Qty x Cost column gives an indication of the "
        "stock value at the selected date but can be different from "
        "the effective stock Valuation since product cost may vary "
        "over time.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self._default_company_id(),
    )

    @api.model
    def _default_product_select(self):
        if self._context.get("active_model") in ["product.product", "product.template"]:
            return "select"
        else:
            return "all"

    @api.model
    def _default_company_id(self):
        return self.env.company

    @api.onchange("import_compatible")
    def _onchange_import_compatible(self):
        self.location_id = False
        self.location_ids = False

    def xls_export(self):
        self.ensure_one()
        report_file = "stock_level_export"
        report_name = "stock_level_xls"
        report = {
            "name": _("Stock Level Export"),
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "report_name": report_name,
            "report_file": report_name,
            "context": dict(self.env.context, report_file=report_file),
            "data": {"wiz_id": self.id},
        }
        return report
