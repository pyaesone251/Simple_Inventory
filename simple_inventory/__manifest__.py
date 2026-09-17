# -*- coding: utf-8 -*-
{
    'name': 'Simple Inventory',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'author': 'Pyae Sone',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_product_view.xml',
        'views/inventory_move_view.xml',
        'views/menu.xml',
    ],
    'sequence':1,
    'installable': True,
    'application': True,
    'auto-install':False,
    'license': 'LGPL-3',
}
