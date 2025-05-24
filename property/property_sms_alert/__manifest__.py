{
    'name': 'Property SMS Alert',
    'version': '1.0',
    'summary': 'Send SMS alerts and value adjustments for property sales',
    'depends': ['base', 'crm_afro_sms', 'advanced_property_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_config_views.xml',
        'views/property_sale_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
}