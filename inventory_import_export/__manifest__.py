# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
{
    'name': 'Inventory Adjustment Import Export Process',
    'version': '15.0.0',
    'summary': """Inventory Adjustment Import Export Process""",
    'description': """
       Inventory Adjustment Import Export Process
    """,
    'author': 'Softprime consulting Pvt Ltd',
    'maintainer': 'Softprime consulting Pvt Ltd',
    'website': 'softprimeconsulting.com',
    'license': 'Other proprietary',
    'category': 'Sales',
    'depends': ['base', 'stock', 'mail', 'report_xlsx',
                'hms_inventory_adjustments'],
    'data': [
        'views/inventory_adjustment.xml',
        'views/report.xml',
    ],
    'demo': [],

    'installable': False,
    'auto_install': False,
}
