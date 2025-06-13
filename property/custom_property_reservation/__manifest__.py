# -*- coding: utf-8 -*-
{
    'name': "Real Estate Reservation",
    'version': '17.0.1.0.0',
    'summary': """
        Property reservation management system with advanced features
        """,
    'description': """
        Real Estate Reservation System Features:
        * Property reservation management
        * Special discount handling
        * Reservation history tracking
        * Cancellation management
        * Extension and transfer features
    """,

    'author': "Ashewa Technologies",
    'website': "https://ashewa.com/",

    'category': 'Sales',

    'depends': [
        'base',
        'ahadubit_property_reservation',
    ],

    'data': [

        
        'security/ir.model.access.csv',

        # Views
       

        'wizard/change_reservation.xml',
        
        'views/main.xml',
      


    ],
    'demo': [
       
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}