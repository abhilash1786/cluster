# -*- coding: utf-8 -*-
# Copyright  Softprime Consulting Pvt Ltd
{
    'name': 'Stock XLSX Report',
    'version': '15.0.0',
    'summary': '',
    'description': '',
    'category': 'stock',
    'author': 'Softprime Consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'depends': ['base', 'stock', 'product'],
    'data': ['security/ir.model.access.csv',
             'views/view_stock_report_db.xml',
             'views/view_stock_detail_report.xml',
             'wizard/view_stock_report_wizard.xml',

             ],
    'demo': [''],
    'auto_install': False,
    'installable': False

}
