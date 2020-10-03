.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================
Vendor Bills - Check duplicates
===============================

This module changes the standard Odoo logic to prevent posting two times the same vendor bill.
The standard logic is too restrictive (blocking) for certain use cases and too permissive for other use cases.

By default a duplicate is detected when there is already an open or paid invoice
with the same vendor and the same vendor bill number ('Reference' field)

In case no vendor bill number has been encoded extra checks are added to detect duplicates :

- same date
- same amount

This logic can be customized via the _get_dup_domain method.

The duplicate checking can be bypassed via the 'Force Encoding' flag.

Known issues / Roadmap
======================

- Align this module with the OCA 'account_invoice_supplier_ref_unique' module.
