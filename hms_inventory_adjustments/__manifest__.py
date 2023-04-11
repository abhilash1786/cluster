# Copyright  Softprime consulting Pvt Ltd
{
    "name": "Inventory Adjustment Process",
    "version": "15.0.0",
    "summary": """Inventory Adjustment Process""",
    "description": """
       Inventory Adjustment Process
    """,
    "author": "Softprime Consulting Pvt Ltd",
    "maintainer": "Softprime consulting Pvt Ltd",
    "website": "softprimeconsulting.com",
    "license": "Other proprietary",
    "category": "Sales",
    "depends": [
        "base",
        "stock",
        "mail",
        "analytic",
        "stock_account",
        "inventory_analytic",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/inventory_adjustment.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
