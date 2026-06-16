# -*- coding: utf-8 -*-
##############################################################################
#
#    Part of myACC. Proprietary and Confidential.
#    © 2026 myACC, IK. All rights reserved.
#
#    See LICENSE file for full copyright and licensing details.
#
#    This module is intended for internal use only and may not be
#    redistributed, copied, or modified without prior written permission
#    from myACC, IK.
#
##############################################################################
{
    "name": "Sale Price per Base UoM",
    "version": "19.0.1.0.0",
    "summary": "Show quotation line price per product base unit (e.g. kg)",
    "description": """
Sale Price per Base UoM
=======================

When a quotation line uses packaging UoM (e.g. drum), the unit price column
shows the price per packaging. This module adds a read-only column with the
catalog price per product base UoM (typically kg), taken from the sales
pricelist rule price.
""",
    "author": "myACC",
    "website": "https://myacc.cloud",
    "category": "Sales",
    "license": "OPL-1",
    "depends": [
        "sale",
        "myacc_access",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
