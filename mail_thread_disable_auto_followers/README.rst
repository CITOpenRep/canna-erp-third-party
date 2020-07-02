.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================================
Disable mail thread auto-followers
==================================

This module allows to disable the automatic addition of followers
for a configurable set of models.

Configuration
=============

Define the system parameter 'mail_thread_disable_auto_followers' with the list of models
for which the automatic addition of followers will be disabled, e.g.
['sale.order', 'purchase.order', 'account.move']
