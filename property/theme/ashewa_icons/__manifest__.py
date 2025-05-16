{
    'name': 'Ashewa base Base',
    'version': '17.0',
    'sequence': 1,
    'summary': 'Ashewa ERP  Base',
    'description': """
        This is a base module for Addis Systems Modules.
            ========================================
    """,
    'category': 'Ashewa ERP /Base',
    'website': 'https://www.addissystems.et/',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'web_editor'],
    'data': [
        'data/ashewa_logo.xml',
        'view/icons_view.xml'
    ],

    'demo': [],
    'post_init_hook': 'update_menu_icons',
    'installable': True,
    'price': 49.99,
    'currency': 'ETB',
    'application': True,
    'auto_install': False,

}
