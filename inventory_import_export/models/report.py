# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
from odoo import fields, models, api, _
from xlwt import easyxf


class Reports(models.AbstractModel):
    _name = 'report.inventory_import_export.export_excel_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):
        """
        generate excel for adjustment template
        """
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        align_value = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        sheet = workbook.add_worksheet('Adjustment Template')
        sheet.write('A1', 'Date', format2)
        sheet.write('B1', 'Location', format2)
        sheet.write('C1', 'Product', format2)
        sheet.write('D1', 'Product Ref', format2)
        sheet.write('E1', 'Category', format2)
        sheet.write('F1', 'Lot/Serial', format2)
        sheet.write('G1', 'Average Cost', format2)
        sheet.write('H1', 'Quantity', format2)
        sheet.write('I1', 'Counted', format2)
        sheet.write('J1', 'Value', format2)
        product_env = self.env['product.product']
        new_row = 2
        lot_env = self.env['stock.production.lot']
        if data:
            argument = [data['company_id']]
            print(data)
            product_sql = """
                select pp.id  from product_product pp left join product_template pt 
                on pp.product_tmpl_id=pt.id where pt.detailed_type='product' and pp.active=true 
                or pt.company_id = %s and pt.company_id is null
                """
            if data.get('category', False):
                argument.append(data['category'])
                product_sql = product_sql + """ and pt.categ_id = %s"""
            self.env.cr.execute(product_sql, tuple(argument))
            product_result = self.env.cr.fetchall()
            if not product_result:
                return True
            product_ids = [x[0] for x in product_result]
            if product_ids:
                for product_id in product_ids:
                    product = product_env.browse(product_id)
                    if product.tracking in ('lot', 'serial'):
                        lot_ids = lot_env.search([('product_id', '=', product.id)])
                        if lot_ids:
                            for lot in lot_ids:
                                sheet.write("A%s" % (new_row), str(data['date']) or "Not Filled", align_value)
                                sheet.write("B%s" % (new_row), str(data['location_name']) or "Not Filled",
                                            align_value)
                                sheet.write("C%s" % (new_row), product.name or "", align_value)
                                sheet.write("D%s" % (new_row), product.default_code or "Not Filled", align_value)
                                sheet.write("E%s" % (new_row), product.categ_id.name or "Not Filled", align_value)
                                sheet.write("F%s" % (new_row), lot.name or ' ', align_value)
                                sheet.write("G%s" % (new_row), product.standard_price or 0.0, align_value)
                                sheet.write("H%s" % (new_row), product.sudo().with_context(
                                    location=data['location_id'], lot_id=lot.id).qty_available or 0.0, align_value)
                                sheet.write("I%s" % (new_row), 0.0, align_value)
                                sheet.write("J%s" % (new_row), 0.0, align_value)
                                new_row += 1
                        else:
                            sheet.write("A%s" % (new_row), str(data['date']) or "Not Filled", align_value)
                            sheet.write("B%s" % (new_row), str(data['location_name']) or "Not Filled",
                                        align_value)
                            sheet.write("C%s" % (new_row), product.name or "", align_value)
                            sheet.write("D%s" % (new_row), product.default_code or "Not Filled", align_value)
                            sheet.write("E%s" % (new_row), product.categ_id.name or "Not Filled", align_value)
                            sheet.write("F%s" % (new_row), "-", align_value)
                            sheet.write("G%s" % (new_row), product.standard_price or 0.0, align_value)
                            sheet.write("H%s" % (new_row), product.sudo().with_context(
                                location=data['location_id']).qty_available or 0.0, align_value)
                            sheet.write("I%s" % (new_row), 0.0, align_value)
                            sheet.write("J%s" % (new_row), 0.0, align_value)
                            new_row += 1
                    else:
                        sheet.write("A%s" % (new_row), data['date'], align_value)
                        sheet.write("B%s" % (new_row), str(data['location_name']) or "Not Filled",
                                        align_value)
                        sheet.write("C%s" % (new_row), product.name or "", align_value)
                        sheet.write("D%s" % (new_row), product.default_code or "Not Filled", align_value)
                        sheet.write("E%s" % (new_row), product.categ_id.name or "Not Filled", align_value)
                        sheet.write("F%s" % (new_row), "-", align_value)
                        sheet.write("G%s" % (new_row), product.standard_price or 0.0, align_value)
                        sheet.write("H%s" % (new_row), product.sudo().with_context(
                            location=data['location_id']).qty_available or 0.0, align_value)
                        sheet.write("I%s" % (new_row), 0.0, align_value)
                        sheet.write("J%s" % (new_row), 0.0, align_value)
                        new_row += 1
