.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Analytic Dimension Policy
=========================

This module adds the *Analytic Dimension Policy* option on Accounts, Account Groups and Account Types.

You have the choice between 3 policies : *Always*, *Never*, *Posted Moves* and *Optional*.

|

If no policy has been defined on an Account the policy will be retrieved from the Account Group or Account Type.

The policy setting is optional on General Accounts and Account Groups and required on Account Types.

|

This is a base module for setting policies on analytical dimensions created by other modules.

Policies will be enforced on all account.move.line fields that have the ``analytic_dimension`` attribure set.

Sample code to do this:

|

.. code-block:: python

   class AccountMoveLine(models.Model):
       _inherit = "account.move.line"

       analytic_account_id = fields.Many2one(analytic_dimension=True)
       department_id = fields.Many2one(
           comodel_name="hr.departmen", string="Department", analytic_dimension=True)

|

.. code-block:: xml

  <record id="view_move_form" model="ir.ui.view">
    <field name="name">account.move.form</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account_analytic_dimension_policy.view_move_form"/>
    <field name="arch" type="xml">
      <xpath expr="//notebook//field[@name='invoice_line_ids']/tree/field[@name='analytic_account_id']" position="after">
        <field name="department_id" force_save="1"
               attrs="{'required': [('analytic_dimension_show', '=', 'required')], 'readonly': [('analytic_dimension_show', '=', 'readonly')]}"/>
      </xpath>
      <xpath expr="//notebook//field[@name='line_ids']/tree/field[@name='analytic_account_id']" position="after">
        <field name="department_id" force_save="1"
               attrs="{'required': [('analytic_dimension_show', '=', 'required')], 'readonly': [('analytic_dimension_show', '=', 'readonly')]}"/>
      </xpath>
    </field>
  </record>

|

This module is inspired by https://github.com/OCA/account-analytic/blob/13.0/account_analytic_required.

