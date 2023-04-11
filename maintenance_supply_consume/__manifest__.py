# -*- coding: utf-8 -*-
# Part of SOFTPRIMECONSULTING PRIVATE LIMITED
{
    'name': 'Maintenance Supply Management',
    'version': '15.0.0.1',
    'summary': 'Maintenance Supply Management',
    'description': 'Maintenance Supply Management',
    'category': 'Custom',
    'author': 'SoftPrime Consulting Pvt Ltd',
    'website': 'http://www.softprimeconsulting.com',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'maintenance',
        'fleet',
        'maintenance_stages',
        'supply_consume_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/location.xml',
        'views/maintenance.xml',
    ],
    'installable': False,
    'auto_install': False,
}