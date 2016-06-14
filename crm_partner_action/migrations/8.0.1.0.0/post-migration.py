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
from openerp.modules.registry import RegistryManager
from openerp import api, pooler, SUPERUSER_ID


def _get_default_company(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        return env['res.company']._company_default_get(
            'crm.partner.action.group')

default_spec = {
    'crm.partner.action.group': [
        ('company_id', 1),

    ],
    'crm.partner.action': [
        ('company_id', 1),
    ]
}


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    openupgrade.set_defaults(cr, registry, default_spec, force=True)  # TODO use _get_default_company
    # openupgrade.set_defaults(cr, registry, {'crm.partner.action.group': [
    #     ('company_id', _get_default_company(cr, registry, 'crm.partner.action.group'))]}, force=False)
