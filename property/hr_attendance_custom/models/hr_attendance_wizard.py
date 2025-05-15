from odoo import models, fields, api
from datetime import timedelta, datetime
import calendar
from odoo.exceptions import UserError


class HrAttendanceWizardLine(models.Model):
    _name = "hr.attendance.wizard.line"
    _description = "Temporary Attendance Record"

    wizard_id = fields.Many2one('hr.attendance.wizard', string="Wizard Reference", required=True, ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    check_in = fields.Datetime(string="Check In", required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    day_name = fields.Char(string="Day Name")
    generated = fields.Boolean(default=False, related="wizard_id.attendance_generated")

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False


class HRAttendanceWizard(models.Model):
    _name = "hr.attendance.wizard"
    _description = "Employee Attendance Wizard"

    name = fields.Char(string="Allocation Name")
    department_ids = fields.Many2many('hr.department', string="Departments")
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    project_ids = fields.Many2many('agent.project', string="Projects")
    location_ids = fields.Many2many('agent.location', string="Location")
    date_from = fields.Date("Start Date", required=True)
    date_to = fields.Date("End Date", required=True)
    attendance_lines = fields.One2many('hr.attendance.wizard.line', 'wizard_id', string="Generated Attendances")
    attendance_generated = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if not vals.get('department_ids') and not vals.get('employee_ids'):
            vals['employee_ids'] = [(6, 0, self.env['hr.employee'].search([]).ids)]
        return super().create(vals)

    @api.onchange('department_ids','project_ids','location_ids', 'date_from', 'date_to')
    def _onchange_department_ids(self):
        """Populate employee_ids based on the selected departments or all employees if no department selected."""
        domain = []
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        if self.project_ids:
            domain.append(('contract_id.project_id', 'in', self.project_ids.ids))
        if self.location_ids:
            domain.append(('contract_id.location_id', 'in', self.location_ids.ids))
        employees = self.env['hr.employee'].search(domain)
        if employees:
            self.employee_ids = [(6, 0, employees.ids)]
        else:
            self.employee_ids = [(5, 0, 0)]


    def create_attendance_records(self):
        """Creates real attendance records from the draft lines."""
        attendance_model = self.env["hr.attendance"]
        for line in self.attendance_lines:
            attendance_model.create({
                'employee_id': line.employee_id.id,
                'check_in': line.check_in,
                'check_out': line.check_out,
            })

    def generate_draft_attendance(self):
        """Generates draft attendance records using employee working hours from resource.calendar.attendance."""
        try:
            self.ensure_one()
            attendance_line_model = self.env["hr.attendance.wizard.line"]

            # Clear previous draft records
            self.attendance_lines.unlink()

            # Use all employees if none specified
            employees = self.employee_ids if self.employee_ids else self.env['hr.employee'].search([])

            for employee in employees:
                contract = employee.contract_id
                if not contract or not contract.resource_calendar_id:
                    raise UserError(f'No contract found for employee: {employee.name}')

                work_schedule = contract.resource_calendar_id

                current_date = self.date_from
                while current_date <= self.date_to:
                    weekday = current_date.weekday()
                    day_name = calendar.day_name[weekday]

                    attendance = work_schedule.attendance_ids.filtered(lambda a: int(a.dayofweek) == weekday)

                    if not attendance:
                        current_date += timedelta(days=1)
                        continue

                    for att in attendance:
                        check_in_time = f"{int(att.hour_from)}:{int((att.hour_from % 1) * 60):02d}:00"
                        check_out_time = f"{int(att.hour_to)}:{int((att.hour_to % 1) * 60):02d}:00"

                        check_in = datetime.combine(current_date, datetime.strptime(check_in_time, "%H:%M:%S").time())
                        check_out = datetime.combine(current_date, datetime.strptime(check_out_time, "%H:%M:%S").time())

                        attendance_line_model.create({
                            'wizard_id': self.id,
                            'employee_id': employee.id,
                            'check_in': check_in,
                            'check_out': check_out,
                            'day_name': day_name,
                        })

                    current_date += timedelta(days=1)
                self.attendance_generated = True
        except Exception as e:
            raise UserError(str(e))

    def create_draft_records(self):
        """Generate attendance records for selected employees or all employees if none selected within the given date range."""
        attendance_model = self.env["hr.attendance"]

        # Use all employees if none specified
        employees = self.employee_ids if self.employee_ids else self.env['hr.employee'].search([])

        for employee in employees:
            current_date = self.date_from
            while current_date <= self.date_to:
                existing_attendance = attendance_model.search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', current_date),
                    ('check_in', '<', current_date + timedelta(days=1))
                ])

                if not existing_attendance:
                    attendance_model.create({
                        'employee_id': employee.id,
                        'check_in': current_date.strftime('%Y-%m-%d 08:00:00'),
                        'check_out': current_date.strftime('%Y-%m-%d 17:00:00'),
                    })
                current_date += timedelta(days=1)

        return {'type': 'ir.actions.act_window_close'}