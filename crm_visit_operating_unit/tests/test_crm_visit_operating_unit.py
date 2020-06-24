# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestCrmVisitOperatingUnit(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.res_users_model = self.env["res.users"]
        self.grp_crm_manager = self.env.ref("crm_visit.group_crm_visit_manager")
        self.grp_crm_user = self.env.ref("crm_visit.group_crm_visit_user")
        self.crm_visit_feeling_model = self.env["crm.visit.feeling"]
        self.crm_visit_reason_model = self.env["crm.visit.reason"]
        self.crm_visit_model = self.env["crm.visit"]

        # Company
        self.company = self.env.ref("base.main_company")

        # Main Operating Unit
        self.ou_main = self.env.ref("operating_unit.main_operating_unit")

        # B2B Operating Unit
        self.ou_b2b = self.env.ref("operating_unit.b2b_operating_unit")

        # B2C Operating Unit
        self.ou_b2c = self.env.ref("operating_unit.b2c_operating_unit")

        # Create user CRM Visit Mananger
        self.user_crm_visit_manager = self._create_user(
            "user_crm_visit_manager",
            [self.grp_crm_manager],
            self.company,
            [self.ou_main, self.ou_b2b, self.ou_b2c],
        )

        # Create user B2B
        self.user_b2b = self._create_user(
            "user_b2b", [self.grp_crm_user], self.company, [self.ou_main, self.ou_b2b]
        )
        # Create user B2C
        self.user_b2c = self._create_user(
            "user_b2c", [self.grp_crm_user], self.company, [self.ou_main, self.ou_b2c]
        )

        # Create Feeling B2B
        self.feeling_b2b = self._create_crm_visit_feeling(
            self.user_crm_visit_manager, "Feeling B2B", self.company, self.ou_b2b
        )
        # Create Feeling B2C
        self.feeling_b2c = self._create_crm_visit_feeling(
            self.user_crm_visit_manager, "Feeling B2C", self.company, self.ou_b2c
        )

        # Create Reason B2B
        self.reason_b2b = self._create_crm_visit_reason(
            self.user_crm_visit_manager, "Reason B2B", self.company, self.ou_b2b
        )
        # Create Reason B2C
        self.reason_b2c = self._create_crm_visit_reason(
            self.user_crm_visit_manager, "Reason B2C", self.company, self.ou_b2c
        )

    def _create_user(self, login, groups, company, operating_units, context=None):
        """
        Create User
        """
        group_ids = [group.id for group in groups]

        return self.res_users_model.create(
            {
                "name": login,
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "operating_unit_ids": [(4, ou.id) for ou in operating_units],
                "groups_id": [(6, 0, group_ids)],
            }
        )

    def _create_crm_visit_feeling(self, user, feeling, company, operating_unit):
        """Create a CRM Visit Feeling"""
        return self.crm_visit_feeling_model.with_user(user.id).create(
            {
                "name": feeling,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
            }
        )

    def _create_crm_visit_reason(self, user, feeling, company, operating_unit):
        """Create a CRM Visit Reason"""
        return self.crm_visit_reason_model.with_user(user.id).create(
            {
                "name": feeling,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
            }
        )

    def test_security(self):
        """Test CRM Visit Feeling Operating Unit Security Rules"""
        # User B2C cannot access CRM Visit Feeling from Unit B2B.
        feeling = self.crm_visit_feeling_model.with_user(self.user_b2c.id).search(
            [("id", "=", self.feeling_b2b.id)]
        )
        self.assertFalse(
            feeling,
            "User %s should not have access to feeling of OU %s"
            % (self.user_b2c.name, self.ou_b2b.name),
        )

        # User B2C cannot access CRM Visit Reason from Unit B2B.
        reason = self.crm_visit_reason_model.with_user(self.user_b2c.id).search(
            [("id", "=", self.reason_b2b.id)]
        )
        self.assertFalse(
            reason,
            "User %s should not have access to reason of OU %s"
            % (self.user_b2c.name, self.ou_b2b.name),
        )
