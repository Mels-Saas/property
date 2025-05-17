{
    'name': 'Property Dashboard',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Custom dashboard for property management with analytics',
    'depends': ['base', 'advanced_property_management','ahadubit_property_base','web'],  # Assuming property_sale contains required models
    'data': [
        'views/property_dashboard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
      
            'property_dashboard/static/src/js/chart_renderer.js',
            'property_dashboard/static/src/js/property_dashboard.js',
            'property_dashboard/static/src/xml/chart_renderer.xml',
            'property_dashboard/static/src/xml/property_dashboard.xml',
            
        ],
      
    },
  
    'installable': True,
    'application': True,
}