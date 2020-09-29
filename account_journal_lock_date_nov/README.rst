.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
account journal lock date
=========================

This module is inspired by the OCA account_journal_lock_date 11.0 module but contains a couple of
significant changes:

- No dependency on 'account_permanent_lock_move'
- By default a lock date on a journal will lock operations for all users,
  including the Financial Advisor (can be relaxed via an inherited module).
