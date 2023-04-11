# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
from odoo import fields, models, api, _
import base64
import logging
from io import BytesIO
_logger = logging.getLogger(__name__)
import xlrd
from odoo.exceptions import UserError, ValidationError


class InventoryAdj(models.Model):
    _inherit = 'res.inventory.adjustment'

    import_file = fields.Binary('Import File', copy=False)

    def import_excel_template(self):
        """
        import excel template for adjustment
        """
        company_id = self.env.company.id
        product = self.env['product.product']
        lot_env = self.env['stock.production.lot']
        date = 0
        qty = 0
        product = 0
        if not self.import_file:
            raise UserError(_('Please add file'))
        val = base64.decodestring(self.import_file)
        fp = BytesIO()
        fp.write(val)
        book = xlrd.open_workbook(file_contents=fp.getvalue())
        sh = book.sheet_by_index(0)
        update_list = []
        location = False
        _logger.info('row count : %d', sh.nrows)
        count = 0
        for line in range(0, sh.nrows):  # sh.nrows
            row = sh.row_values(line)
            try:
                update_list.append(row[0].lower().rstrip(' '))
                update_list.append(row[1].lower().rstrip(' '))
                update_list.append(row[2].lower().rstrip(' '))
                update_list.append(row[3].lower().rstrip(' '))
                update_list.append(row[4].lower().rstrip(' '))
                update_list.append(row[5].lower().rstrip(' '))
                update_list.append(row[6].lower().rstrip(' '))
                update_list.append(row[7].lower().rstrip(' '))
                update_list.append(row[8].lower().rstrip(' '))
                update_list.append(row[9].lower().rstrip(' '))
            except:
                raise UserError(('Please add Header in Excel sheet '))
            try:
                date = update_list.index('date')
                product = update_list.index('product')
                code = update_list.index('product ref')
                qty = update_list.index('quantity')
                count_qty = update_list.index('counted')
                location = update_list.index('location')
                lot_serial = update_list.index('lot/serial')
                break
            except Exception as e:
                raise UserError(
                    _('Import xls file header is not correct!. Please correct it first and then re import !'))
        self.adjustment_line = False
        lot_id = False
        for line in range(1, sh.nrows):  # sh.nrows
            count += 1
            row = sh.row_values(line)
            location_id = self.env['stock.location'].search([('complete_name', '=', row[location])])
            if location_id.id != self.location_id.id:
                raise UserError(_('location in Excel and location selected during import is different!'))
            domain = [
                ('detailed_type', '=', 'product'),
                ('default_code', '=', row[code])
            ]
            product_id = self.env['product.product'].search(domain)
            if not product_id:
                domain.pop(1)
                domain += [('name', '=', row[product])]
            product_id = self.env['product.product'].search(domain)
            if not product_id:
                raise ValidationError(_('This %s product is not found') % (row[product]))
            if product_id and len(product_id) < 1:
                raise ValidationError(_('Multiple product find of %s') % (row[product]))
            if row[count_qty] < 0:
                raise UserError(_('Counted Qty is Negative'))
            on_hand_qty = product_id.sudo().with_context(location=self.location_id.id).qty_available
            if row[lot_serial]:
                domain_lot = [
                    ('product_id', '=', product_id.id),
                    ('name', '=', row[lot_serial])
                ]
                if self.env.user.has_group('base.group_multi_company'):
                    domain_lot.append(('company_id', '=', company_id))
                lot_serial_id = lot_env.search(domain_lot)
                if lot_serial_id:
                    lot_id = lot_serial_id.id
                    on_hand_qty = product_id.sudo().with_context(lot_id=lot_serial_id.id,
                                                                location=self.location_id.id).qty_available
            if float(row[count_qty]) == 0.0:
                product_qty = 0.0
            elif on_hand_qty == 0.0:
                product_qty = row[count_qty]
            else:
                product_qty = on_hand_qty - ((float(row[qty]) - row[count_qty]))
            adjustment_line = self.env['inventory.adjustment.line'].sudo(). \
                create({'adjustment_id': self.id,
                        'product_id': product_id.id,
                        'counted': product_qty,
                        'lot_id': lot_id,
                        'onhand_qty': on_hand_qty,
                        'company_id': self.company_id.id,
                        })
            if adjustment_line:
                adjustment_line.onchange_product_id()

    def print_export_template(self):
        """
        generate inventory adjustment template
        """
        context = self._context
        data = {
            'ids': self.ids,
            'model': self._name,
            'location_id': self.location_id.id,
            'location_name': self.location_id.complete_name,
            'date': self.date,
            'category': self.category_id.id,
            'company_id': self.company_id.id}
        return self.env.ref('inventory_import_export.action_inventory_adjustment_template').report_action(self, data=data)
