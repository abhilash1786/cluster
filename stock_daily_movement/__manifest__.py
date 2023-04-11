# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Stock Daily Movement',
    'version': '15.0.0',
    'summary': 'Stock Daily Movement Database View',
    'description': 'Stock Daily Movement Database View',
    'category': 'stock',
    'author': 'Softprime Consulting Pvt Ltd',
    'website': 'https://softprimeconsulting.com/',
    'license': 'Other proprietary',
    'depends': ['stock', 'product', 'base'],
    'data': ['security/ir.model.access.csv',
             'wizard/view_stock_movement_wiz.xml',
             'views/view_stock_movement_db.xml'],
    'installable': False,
    'auto_install': False
}