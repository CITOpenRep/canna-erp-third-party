.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Analytic Dimension Policy
=========================

This module adds the *Analytic Dimension Policy* option on Accounts, Account Groups and Account Types.

You have the choice between 4 policies : *Always*, *Never*, *Posted Moves* and *Optional*.

|

If no policy has been defined on an Account the policy will be retrieved from the Account Group or Account Type.

The policy setting is optional on General Accounts and Account Groups and required on Account Types.

You can also define on Account, Account Group or Account Type for which dimensions the policy will be enforced.
By default all Analytic Dimensions will be enforced.

|

Policies will be enforced on all account.move.line fields that have been defined as an analytic_dimension via
Accounting | Invoicing -> Configuration -> Analytic Dimensions.

|

This is a base module for setting policies on analytical dimensions created by other modules.

Sample code to do this:

|

.. code-block:: python

   class AccountMoveLine(models.Model):
       _inherit = "account.move.line"

       department_id = fields.Many2one(
           comodel_name="hr.department", string="Department")

|

.. code-block:: xml

  <record id="view_move_form" model="ir.ui.view">
    <field name="name">account.move.form</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account_analytic_dimension_policy.view_move_form"/>
    <field name="arch" type="xml">
      <xpath expr="//notebook//field[@name='invoice_line_ids']/tree/field[@name='analytic_account_id']" position="after">
        <field name="department_id"/>
      </xpath>
      <xpath expr="//notebook//field[@name='line_ids']/tree/field[@name='analytic_account_id']" position="after">
        <field name="department_id"/>
      </xpath>
    </field>
  </record>

|

Please not that this view MUST inherit from the "account_analytic_dimension_policy.view_move_form" to enable view based policy enforcement.

|

Dimensions that are not available in the standard bank reconciliation widget must also be added to the widget Qweb template.

|

.. code-block:: xml

  <t t-extend="reconciliation.line.create">

    <t t-jquery="tr[class='create_tax_id']" t-operation="append">
      <tr class="create_department_id">
        <td class="o_td_label">
          <label class="o_form_label">Department</label>
        </td>
        <td class="o_td_field"></td>
      </tr>
    </t>

  </t>

|

This module is inspired by https://github.com/OCA/account-analytic/blob/13.0/account_analytic_required.

|

