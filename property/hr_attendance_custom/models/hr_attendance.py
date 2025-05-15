from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_approved = fields.Boolean(string="Approved", default=False)
    project_id = fields.Many2one('agent.project', related="employee_id.contract_id.project_id", store=True, string="Project")
    status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
        ],
        string="Status",
        default="pending"
    )

    def action_approve_attendance_1(self):
        for rec in self:
            rec.is_approved = True
            rec.status = 'approved'  
        
