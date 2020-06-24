# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestCrmVisitOperatingUnit(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.res_groups = self.env["res.groups"]
        self.res_users_model = self.env["res.users"]
        self.crm_visit_feeling_model = self.env["crm.visit.feeling"]
        self.crm_visit_reason_model = self.env["crm.visit.reason"]
        self.crm_visit_model = self.env["crm.visit"]
        self.res_company_model = self.env["res.company"]
        self.operating_unit_model = self.env["operating.unit"]

        # Company
        self.company = self.env.ref("base.main_company")

        # Main Operating Unit
        self.ou_main = self.env.ref("operating_unit.main_operating_unit")

        # Unit1 Operating Unit
        self.ou_unit1 = self.env.ref("operating_unit.operating_unit_1")

        # Unit2 Operating Unit
        self.ou_unit2 = self.env.ref("operating_unit.operating_unit_2")

        # Create user1
        self.user1 = self._create_user(
            "user_1", [self.grp_sale_user], self.company, [self.ou1, self.ou_unit1]
        )
        # Create user2
        self.user2 = self._create_user(
            "user_2", [self.grp_sale_user], self.company, [self.ou_unit2]
        )

        # Create Feeling1
        self.feeling1 = self._create_crm_visit_feeling(
            "Feeling1", self.company, self.ou_unit1
        )
        # Create Feeling2
        self.feeling2 = self._create_crm_visit_feeling(
            "Feeling2", self.company, self.ou_unit2
        )

        # Create Reason1
        self.reason1 = self._create_crm_visit_reason(
            "Reason1", self.company, self.ou_unit1
        )
        # Create Reason2
        self.reason2 = self._create_crm_visit_reason(
            "Reason2", self.company, self.ou_unit2
        )

    def _create_user(self, login, groups, company, operating_units, context=None):
        """
        Create User
        """
        group_ids = [group.id for group in groups]

        return self.res_users_model.create(
            {
                "name": "Test Crm Visit User",
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "operating_unit_ids": [(4, ou.id) for ou in operating_units],
                "groups_id": [(6, 0, group_ids)],
            }
        )

    def _create_crm_visit_feeling(self, uid, feeling, company, operating_unit):
        """Create a CRM Visit Feeling"""
        return self.crm_visit_feeling_model.sudo(uid).create(
            {
                "name": feeling,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
            }
        )

    def _create_crm_visit_reason(self, uid, feeling, company, operating_unit):
        """Create a CRM Visit Reason"""
        return self.crm_visit_reason_model.sudo(uid).create(
            {
                "name": feeling,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
            }
        )

    def _create_crm_visit(self, uid, feeling, reason, company, operating_unit):
        """Create a CRM Visit"""
        return self.crm_visit_model.sudo(uid).create(
            {
                "name": feeling,
                "feeling_id": feeling.id,
                "reason_id": reason.id,
                "company_id": company.id,
                "operating_unit_id": operating_unit.id,
            }
        )

    def test_security(self):
        """Test Crm Visit Feeling Operating Unit Security Rules"""
        # User 2 is only assigned to Operating Unit 2, and cannot
        # Access CRM Visit Feeling from Main Operating Unit or Unit 1.
        feelings = self.crm_visit_feeling_model.sudo(self.user2.id).search(
            [("id", "=", self.feeling1.id), ("operating_unit_id", "=", self.ou1.id)]
        )
        self.assertEqual(
            feelings.ids,
            [],
            "User 2 should not have access to " "OU %s" % self.ou1.name,
        )

        reasons = self.crm_visit_reason_model.sudo(self.user2.id).search(
            [("id", "=", self.reason1.id), ("operating_unit_id", "=", self.ou1.id)]
        )
        self.assertEqual(
            reasons.ids, [], "User 2 should not have access to " "OU %s" % self.ou1.name
        )
