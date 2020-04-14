# Copyright 2009-2018 Noviat
# Copyright OpenUpgrade contributors (https://github.com/oca/openupgradelib)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

column_renames = {
    "sale_discount_rule": [("discount", "discount_pct", "Discount Percentage")]
}


def rename_columns(cr, column_spec):
    for table in column_spec.keys():
        for (old, new, comment) in column_spec[table]:
            cr.execute(
                "SELECT column_name "
                "FROM information_schema.columns "
                "WHERE table_name=%s "
                "AND column_name=%s",
                (table, new),
            )
            res = cr.fetchone()
            if not res:
                _logger.info("table %s, column %s: renaming to %s", table, old, new)
                cr.execute(
                    'ALTER TABLE "{}" RENAME "{}" TO "{}"'.format(table, old, new)
                )
                cr.execute('DROP INDEX IF EXISTS "{}_{}_index"'.format(table, old))
                if comment:
                    cr.execute(
                        "COMMENT ON COLUMN {}.{} IS '{}'".format(table, new, comment)
                    )


def migrate(cr, version):
    if not version:
        return
    rename_columns(cr, column_renames)
