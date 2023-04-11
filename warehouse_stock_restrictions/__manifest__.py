# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
{
    "name": "Warehouese location restriction",
    "version": "15.0.0",
    "summary": """Warehouese location restriction""",
    "description": """
        Warehouese location restriction
    """,
    "author": "Softprime Consulting Pvt Ltd",
    "maintainer": "Softprime Consulting Pvt Ltd",
    "website": "softprimeconsulting.com",
    "license": "Other proprietary",
    "category": "Inventory",
    "depends": ["base", "stock", "product"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/users_view.xml",
    ],
    "installable": False,
    "auto_install": False,
}
