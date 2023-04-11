# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    "name": "Readonly Onhand qty",
    "version": "15.0.0",
    "category": "Stock",
    "sequence": 3,
    "summary": """
        This module show details of on hand qty without editable.
    """,
    "author": "Softprime Consulting Pvt Ltd",
    "maintainer": "Softprime Consulting Pvt Ltd",
    "website": "softprimeconsulting.com",
    "license": "Other proprietary",
    "company": "Softprime Consulting Pvt Ltd",
    "depends": ["stock", "product", "stock_account"],
    "data": [
        "views/product_views.xml",
        "views/stock_quant.xml",
        "security/security.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
