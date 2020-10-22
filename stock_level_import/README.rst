.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
Stock Level import
==================

This module adds a button on the ‘Inventory’ screen to allow the import of the inventory lines from an excel file.

Before starting the import a number of sanity checks are performed:

- check if the stock locations are correct
- check if the products are correct
- check if the product UOMs are correct

If no issues are found the inventory lines will be loaded.

The excel file must have a header line with the following fields:

- Stock Location (or location_id, cf. stock_level_export_xls)
- Product (or product_id, cf. stock_level_export_xls)
- Product UOM (or product_uom_id, cf. stock_level_export_xls))
- Quantity

Optional fields:
- prod_lot_id (Lot/Serial number
- package_id (Pack)
- partner_id (Owner)

The output of the 'stock_level_export_xls' module is compatible with the input format of this module.

The combination of these two modules (available from apps.odoo.com) gives a simple yet powerful
tool for inventory updates. 

Roadmap / Known issues
======================

No known issues at this point in time.

Assistance
==========

Contact info@noviat.com if you require support or functional extensions for this module.
