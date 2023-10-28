# -*- coding: utf-8 -*-

from odoo import models, fields

class CasualWorkers(models.Model):
    _name = "casual.workers"
    _inherit = "hr.employee"
    
    available_project_labour = fields.Boolean('Available Project Labour')
    bank_name = fields.Char("Bank Name")
    
    def _run_reset_available_workers(self):
        casual_worker_ids = self.env['casual.workers'].search([('available_project_labour', '=', True)])
        for casual_worker_id in casual_worker_ids:
            casual_worker_id.write({'available_project_labour': False})