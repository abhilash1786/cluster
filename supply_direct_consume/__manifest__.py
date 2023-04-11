# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Supply direct consume',
    'version': '15.0.0',
    'summary': """Supply direct consume""",
    'description': """
        Supply direct consume
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Inventory',
    'depends': ['supply_consume_management', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/material_transfer.xml',
        'views/material_issue.xml',
        'views/res_setting.xml',

        'menu/menu.xml',

    ],
    'installable': False,
    'auto_install': False,
}
