.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================
Import Price Catalog
====================

Module to import Price Catalogs.

The file to be imported must have the following headers:
- productcode
- productdescription
- price

productdescription is not used but kept for legacy compatibility.

The file must be a csv file with the following settings:
- character set: utf-8
- field delimiter: ;
- string delimiter: "

TODO:
- Remove dependencies on price_catalog_sale and price_catalog_purchase.
