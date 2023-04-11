# -*- coding: utf-8 -*-
# Part of Softprime Consulting Pvt Ltd.
{
    'name': 'Supply Management Unit Restriction',
    'version': '15.0.0',
    'category': 'Custom',
    'sequence': 1,
    'summary': 'Supply Management Unit Restriction',
    "author": "Softprime Consulting Pvt Ltd",
    'description': """
    Supply Management Unit Restriction
    """,
    'website': 'https://softprimeconsulting.com',
    'depends': ['base', 'stock', 'supply_consume_management', 'product'],
    'data': [
        'views/product_template.xml',
        'views/supply_material_consume_view.xml',
        'views/supply_direct_consume.xml'
    ],
    'demo': [],
    'test': [],
    'installable': False,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
}
