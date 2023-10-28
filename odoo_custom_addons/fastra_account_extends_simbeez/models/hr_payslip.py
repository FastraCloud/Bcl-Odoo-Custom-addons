# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    prelims_category_id = fields.Many2one('prelims.category', string="Project Stage")