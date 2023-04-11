# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    "name": "Internal Material Transfer",
    "version": "15.0.0",
    "summary": """Internal Material Transfer""",
    "description": """
        Internal Material Transfer allow to stock exchange between
        locations based on request approval process.
    """,
    "author": "Softprime Consulting Pvt Ltd",
    "maintainer": "Softprime Consulting Pvt Ltd",
    "website": "softprimeconsulting.com",
    "license": "Other proprietary",
    "category": "Inventory",
    "depends": ["base", "stock", "analytic", "stock_xlsx_report"],
    "data": [
        "data/sequence.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "report/supply_material_request_action.xml",
        "report/supply_material_request_report.xml",
        "report/pending_material_issue_action.xml",
        "report/pending_material_issue_report.xml",
        "views/internal_material_request_view.xml",
        "views/res_config_setting.xml",
        "views/user_setting_view.xml",
        "views/material_issue.xml",
        "views/stock_view.xml",
        "views/stock_quant.xml",
        "views/stock_report.xml",
        "menu/menu.xml",
    ],
    "installable": False,
    "auto_install": False,
}
