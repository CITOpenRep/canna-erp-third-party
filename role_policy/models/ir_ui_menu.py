# Copyright 2020-2021 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, tools
from odoo.tools import config

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    role_ids = fields.Many2many(
        comodel_name="res.role",
        relation="res_role_menu_rel",
        column1="menu_id",
        column2="role_id",
        string="Roles",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.context.get("role_policy_init") and "groups_id" in vals:
                del vals["groups_id"]
            if "role_ids" in vals:
                roles = self.env["res.role"].browse(vals["role_ids"][0][2])
                vals["groups_id"] = [(6, 0, [x.id for x in roles.mapped("group_id")])]
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("role_policy_init") and "groups_id" in vals:
            del vals["groups_id"]
        res = super().write(vals)
        if "role_ids" in vals:
            for menu in self:
                menu.groups_id = menu.role_ids.mapped("group_id")
        return res

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        """
        Hide all menus without the role_group(s) or the user.
        """
        if self.env.user.exclude_from_role_policy or config.get("test_enable"):
            visible_ids = self._visible_menu_ids_user_admin(debug=debug)
        else:
            visible_ids = super()._visible_menu_ids(debug=debug)
            user_roles = self.env.user.enabled_role_ids or self.env.user.role_ids
            user_groups = user_roles.mapped("group_id")
            menus = self.browse()
            for menu in self.browse(visible_ids):
                for group in menu.groups_id:
                    if group in user_groups:
                        menus |= menu
                        continue

            # remove menus without action menu
            action_menus = menus.filtered(lambda m: m.action and m.action.exists())
            # folder_menus = menus - action_menus
            filtered_ids = []

            def get_parent_ids(menu, menu_ids):
                parent = menu.parent_id
                if parent:
                    if parent in menus:
                        menu_ids.append(parent.id)
                        return get_parent_ids(parent, menu_ids)
                    else:
                        return []
                else:
                    return menu_ids

            for menu in action_menus:
                filtered_ids += get_parent_ids(menu, [menu.id])

            visible_ids = set(filtered_ids)
        return visible_ids

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids_user_admin(self, debug=False):
        """
        Same logic as in base/models/ir_ui_menu.py but we ignore
        the role groups for user_root and user_admin.
        """
        # retrieve all menus, and determine which ones are visible
        context = {"ir.ui.menu.full_list": True}
        menus = self.with_context(context).search([])

        groups = self.env.user.groups_id
        if not debug:
            groups = groups - self.env.ref("base.group_no_one")
        # first discard all menus with groups the user does not have
        menus = menus.filtered(
            lambda menu: not menu.groups_id.filtered(lambda r: not r.role)
            or menu.groups_id & groups
        )

        # take apart menus that have an action
        action_menus = menus.filtered(lambda m: m.action and m.action.exists())
        folder_menus = menus - action_menus
        visible = self.browse()

        # process action menus, check whether their action is allowed
        access = self.env["ir.model.access"]
        MODEL_GETTER = {
            "ir.actions.act_window": lambda action: action.res_model,
            "ir.actions.report": lambda action: action.model,
            "ir.actions.server": lambda action: action.model_id.model,
        }
        for menu in action_menus:
            get_model = MODEL_GETTER.get(menu.action._name)
            if (
                not get_model
                or not get_model(menu.action)
                or access.check(get_model(menu.action), "read", False)
            ):
                # make menu visible, and its folder ancestors, too
                visible += menu
                menu = menu.parent_id
                while menu and menu in folder_menus and menu not in visible:
                    visible += menu
                    menu = menu.parent_id

        return set(visible.ids)
