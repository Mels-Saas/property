{
    'name': 'HR Attendance Customization',
    'version': '1.0',
    'summary': 'Customizes HR Attendance and Payslip functionality',
    'depends': ['hr', 'hr_attendance','om_hr_payroll','edomias_agent'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_views.xml',
        'views/hr_attendance_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}