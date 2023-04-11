# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    'name': 'Supply Returns',
    'version': '13.0.0.1',
    'summary': 'Supply Returns',
    'description': 'Supply Returns',
    'category': 'inventory',
    'author': 'SOFTPRIMECONSULTING PRIVATE LIMITED',
    'website': 'softprimeconsulting.com',
    'license': 'OPL-1',
    'depends': [
        'supply_material_request',
        'supply_consume_management',
        'supply_direct_consume',
    ],
    'data': [
        'security/security.xml',

        'view/material_transfer.xml',
        'view/material_issue.xml',
        'view/material_consume.xml',

        'menu/menu.xml',
    ],
    'installable': False,
    'auto_install': False,
}
