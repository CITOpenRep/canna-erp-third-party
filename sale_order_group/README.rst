.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================
Sale Order Group
================

This module allows to create a group of linked sales orders.

Only draft orders for the same Customer can be linked together.
Linked orders can no longer be confirmed nor cancelled individually.
An order must be removed from the group before an individual confirm or cancel
operation is allowed.
