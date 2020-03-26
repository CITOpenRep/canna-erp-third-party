# Copyright 2016-2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import base64
from tempfile import TemporaryFile


class ImportPriceCatalog(models.TransientModel):
    _name = 'import.price.catalog'
    _description = 'Import Price Catalogs'

    data = fields.Binary('File', required=True)
    subcatalog_id = fields.Many2one(
        comodel_name='price.subcatalog', string='Subcatalog', required=True)
    company_id = fields.Many2one('res.company', 'Company')
    remove_data = fields.Boolean('Remove All Data')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list=fields_list)
        if 'company_id' in fields_list:
            company = self.env['res.company'].search([])
            defaults.update({'company_id': company[0].id})
        return defaults

    def import_catalog(self):
        error_mess = 'Errors: ' + chr(10)
        product = self.env['product.product']
        catalog_item = self.env['price.catalog.item']
        obj_model = self.env['ir.model.data']

        # Add checkbox and delete entries existing in catalog before importing.
        if self.remove_data:
            catalog_data_delete = catalog_item.search([(
                'subcatalog_id', '=', self.subcatalog_id.id)])
            for item in catalog_data_delete:
                item.unlink()

        # Input file
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(self.data).decode("utf-8"))

        DELIMITER = ';'
        status_report = ''
        fileobj.seek(0)
        line = fileobj.readline().strip().replace('"', '')  # First line
        # print line
        keys = line.split(DELIMITER)
        line = fileobj.readline().strip().replace('"', '')
        # print line
        problem_count = 0

        while len(line) > 0:
            values = line.split(DELIMITER)
            dic = dict(zip(keys, values))
            product_id = False
            # Determine search arguments based on input
            # product_search_args = [('wholesale_id','=',wholesale.id)]
            if 'productcode' in dic and dic['productcode']:
                product_search_args = [
                    ('default_code', '=', dic['productcode'])]
                product_id = product.search(product_search_args)

            if product_id:
                product_id = product_id[0]
                item_row = {
                    'subcatalog_id': self.subcatalog_id.id,
                    'product_id': product_id.id,
                    'price': dic['price'],
                }
                catalog_item.create(item_row)
            else:
                problem_count += 1
                # Create new code
                error_mess = error_mess + 'productcode:' + dic[
                    'productcode'] + ' not found' + chr(10)
                # print 'productcode:' , dic['productcode'], ' not found'
            # Read next line
            line = fileobj.readline().strip().replace('"', '')
        # All went well
        if problem_count == 0:
            status_report = 'No Problems Occured'
        # Problems occured
        elif problem_count > 0:
            status_report = error_mess
        fileobj.close()
        model_data_ids = obj_model.search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'data_price_catalog_view_form')]
        )
        assert len(model_data_ids), ("Could not find the "
                                     "data.price.catalog.form view.")
        resource_id = model_data_ids.read(fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'data.price.catalog',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.with_context(status_report=status_report)._context,
        }


class DataPriceCatalog(models.TransientModel):
    _name = 'data.price.catalog'
    _description = 'Data Price Catalog'
    status_report = fields.Text('Report')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list=fields_list)
        if self._context.get('status_report', False):
            defaults.update({'status_report': self._context['status_report']})
        return defaults
