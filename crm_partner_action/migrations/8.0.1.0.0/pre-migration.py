# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Onestein
#    (<http://www.onestein.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openupgradelib import openupgrade
import logging
logger = logging.getLogger('OpenUpgrade')

column_renames = {
    'res_partner_action': [
        ('contact', 'main_partner_id'),
        ('user_actor', 'followup_user_id'),
        ('user_creator', 'user_id'),
        ('action_group', 'action_group_id'),
    ]
}

model_renames = [
    ('res.partner.action', 'crm.partner.action'),
    ('res.partner.action.group', 'crm.partner.action.group')
]

table_renames = [
    ('res_partner_action', 'crm_partner_action'),
    ('res_partner_action_group', 'crm_partner_action_group')
]


def convert_str_to_int_datatype(cr):
    cr.execute(
        """
        SELECT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = 'crm_partner_action'
        AND column_name = 'action_group_id'
        );
        """
    )
    res = cr.fetchone()
    if res == 't':
        logger.info('action_group_id', res)
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE crm_partner_action ALTER COLUMN action_group_id
            SET DATA TYPE int USING action_group_id::integer;
            """
        )



@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    openupgrade.rename_models(cr, model_renames)
    openupgrade.rename_columns(cr , column_renames)
    openupgrade.rename_tables(cr, table_renames)
    convert_str_to_int_datatype(cr)
