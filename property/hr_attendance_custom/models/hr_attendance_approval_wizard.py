from odoo import models, fields, api


class HrAttendanceApprovalWizard(models.TransientModel):
    _name = 'hr.attendance.approval.wizard'
    _description = 'Attendance Approval Wizard'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    attendance_ids = fields.One2many('hr.attendance', string="Attendances", compute="_compute_attendances")
    show_attendances = fields.Boolean(string="Show Attendances", default=False)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_attendances(self):
        for wizard in self:
            wizard.attendance_ids = self.env['hr.attendance'].search([
                ('employee_id', '=', wizard.employee_id.id),
                ('check_in', '>=', wizard.date_from),
                ('check_in', '<=', wizard.date_to),
                ('is_approved', '=', False),
            ])
            wizard.show_attendances = bool(wizard.attendance_ids)

    def action_fetch_attendances(self):
        self._compute_attendances()

    def action_approve_attendances(self):
        self.attendance_ids.write({'is_approved': True})
        return {'type': 'ir.actions.act_window_close'}