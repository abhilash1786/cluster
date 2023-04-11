# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Supply Direct consume Approval process',
    'version': '15.0.0',
    'summary': """Supply Direct consume Approval process""",
    'description': """
        Supply Direct consume Approval process
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Inventory',
    'depends': ['supply_request_approval', 'supply_direct_consume'],
    'data': [
        'views/material_view.xml',
    ],
    'installable': False,
    'auto_install': False,
}
