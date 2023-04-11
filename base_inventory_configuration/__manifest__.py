# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
{
    'name': 'Base Inventory configurations',
    'version': '16.0',
    'summary': """Base Inventory configurations""",
    'description': """
        Base Inventory configurations for warehouse, product, location etc.
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Inventory',
    'depends': ['base', 'stock', 'product', 'stock_account'],
    'data': [
        'views/location_master_view.xml',
    ],
    'demo': [],

    'installable': True,
    'auto_install': True,
}
