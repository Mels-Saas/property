{
    "name": "Custom Project Notifications",
    "version": "1.0",
    "category": "Project",
    "summary": "Send SMS notifications on task assignments and state changes.",
    "license": "AGPL-3",
    "author": "Yeabsra Ayehualem",
    "depends": ["base", 'sms','mass_mailing','mass_mailing_sms'],
    "data": [
        "security/ir.model.access.csv",
        "views/afro_message_config_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
