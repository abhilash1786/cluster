# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Supply Material Purchase Request',
    'version': '15.0.0',
    'summary': """Supply Material Purchase Request""",
    'description': """
        Supply Material Purchase Request
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Inventory',
    'depends': ['base', 'stock', 'supply_material_request', 'sp_purchase_request'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_pr.xml',
        'views/material_req.xml',
    ],
    'demo': [],

    'installable': False,
    'auto_install': False,
}
