# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
{
    'name': 'Landed Cost Addons',
    'category': 'Custom',
    'version': '15.0.1',
    'summary': 'Landed Cost',
    'description': """
        Landed Cost Addons
    """,
    'author': 'Softprime Consulting Pvt Ltd',
    'website': 'http://www.softprimeconsulting.com',
    'company': 'Softprime Consulting Pvt Ltd',
    'license': 'Other proprietary',
    'depends': [
        'account',
        'stock_landed_costs'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/landed_cost_security.xml',
        'wizard/landed_cost_approve_wizard.xml',
        'report/landed_cost_report.xml',
        'report/report_action.xml',
        'view/res_config_setting.xml',
        'view/stock_landed_cost.xml',
        'view/email_template.xml',
    ],
    'installable': False,
    'application': True,
}
