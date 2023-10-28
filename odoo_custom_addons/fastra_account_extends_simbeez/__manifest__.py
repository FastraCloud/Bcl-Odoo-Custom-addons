# -*- coding: utf-8 -*-
{
    'name': "Fastra Account Extends Simbeez",

    'summary': """
        Changes of Rename Prelims Category to Project Stages
    """,
    'description': """
        Changes of Rename Prelims Category to Project Stages
    """,
    
    'depends': ['od_material_consumption','account','purchase', 'hr_payroll'],
    'data': [
        'views/account.xml',
        'views/purchase.xml',
        'views/material_consumption.xml',
        'views/hr_payslip.xml',
    ],
    
    'installable' : True,
}
