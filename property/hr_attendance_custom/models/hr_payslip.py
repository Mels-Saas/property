from odoo import models, fields, api
from odoo.exceptions import ValidationError


# class HrPayslip(models.Model):
#     _inherit = 'hr.payslip'
#
#     def action_payslip_done(self):
#         attendances = self.env['hr.attendance'].search([
#             ('employee_id', '=', self.employee_id.id),
#             ('is_approved', '=', False),
#         ])
#         if attendances:
#             raise ValidationError("Cannot process payroll until all attendances are approved.")
#
#         if (
#             not self.env.context.get("without_compute_sheet")
#             and not self.prevent_compute_on_confirm
#         ):
#             self.compute_sheet()
#         return self.write({"state": "done"})