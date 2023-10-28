# -*- coding: utf-8 -*-

{
    'name': 'HR Extends',
    'version': '1.0',
    'description': """
HR Extends
===================================================
""",
    'depends': ['hr','hr_payroll_account', 'project_costing', 'fastra_account_extends_simbeez'],
    'data': [
        'security/ir.model.access.csv',
        'data/casual_worker_cron.xml',
        'data/sequence.xml',
        
        'views/hr_casual_worker.xml',
        'views/hr_payroll.xml',
        'views/project_labor_view.xml',

        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': True,
}
