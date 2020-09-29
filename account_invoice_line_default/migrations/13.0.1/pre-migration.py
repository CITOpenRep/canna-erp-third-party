# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        SELECT id FROM ir_model_fields
          WHERE name='property_in_inv_account_id'
          AND model='res.partner';
        """
    )
    res = cr.fetchall()
    field_id = res[0][0]
    cr.execute(  # pylint: disable=E8103
        """
        UPDATE ir_property
          SET name='property_in_inv_account_id', fields_id=%s
          WHERE name='property_in_inv_account_id';
        UPDATE ir_property
          SET name='property_out_inv_account_id', fields_id=%s
          WHERE name='property_out_inv_account_id';
        """
        % (field_id, field_id)
    )
