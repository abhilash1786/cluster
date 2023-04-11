# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Supply Material Approval process',
    'version': '15.0.0',
    'summary': """Supply Material Approval process""",
    'description': """
        Supply Material Approval process
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Inventory',
    'depends': ['supply_consume_management', 'account'],
    'data': [

        'security/security_view.xml',
        'security/ir.model.access.csv',

        'wizard/change_approver_name_view.xml',

        'views/material_view.xml',
        'views/user.xml',

        'menu/menu.xml',
    ],
    'installable': False,
    'auto_install': False,
}
