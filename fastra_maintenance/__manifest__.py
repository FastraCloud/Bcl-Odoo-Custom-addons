{
    'name': 'Maintenance - Fastra',
    'version': '1.0',
    'summary': 'Maintenance',
    'description': 'Maintenance',
    'depends': ['analytic'],
    'data': [
        'security/ir.model.access.csv',

        'views/asset_registration.xml',
        'views/register_asset_maintenance_cost.xml',
        'views/asset_movement.xml',
        'views/asset_report.xml',

        'wizards/asset_report.xml',
    ],
    'installable': True,
    'auto_install': False
}
