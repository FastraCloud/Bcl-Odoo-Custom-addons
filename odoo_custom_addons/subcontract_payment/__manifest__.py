# -*- coding: utf-8 -*-

{
    'name': 'Sub-Contract Payment',
    'version': '1.0',
    'description': """
Sub-Contract Payment
===================================================
""",
    'depends': ['account','account_voucher', 'project_costing', 'od_material_consumption', 'purchase_stock',
                ],
    'data': [
        'data/ir_sequence_data.xml',
        
        'security/ir.model.access.csv',
        
        'views/subcontract_payment.xml',
        'views/subcontractor_labour.xml',
        'views/plant_cost.xml',
        'views/subcontractor_block_work.xml',
        'views/iron_bender.xml',
        'views/subcontractor_bill.xml',
        'views/subcontractor_bill_payment.xml',
        'views/subcontractor_purchase.xml',
        'views/res_partner.xml',
        # 'views/project_costing.xml',
    ],
    'installable': True,
    'auto_install': True,
}
