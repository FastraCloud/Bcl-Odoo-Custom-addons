# -*- coding: utf-8 -*-

{
    'name': 'Lock Dates',
    'version': '1.0',
    'description': """
Lock Dates
===================================================
""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',

        'views/lock_date.xml',
    ],
    'installable': True,
    'auto_install': False,
}
