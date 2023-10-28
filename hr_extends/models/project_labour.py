# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_tax_id = fields.Many2one('account.tax', 'Tax')
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])
    journal_id = fields.Many2one('account.journal', string='Journal')


class ProjectLabour(models.Model):
    _inherit = "project.labour"
    _rec_name = "name"

    def get_default_account_tax(self):
        return self.env.user.company_id.account_tax_id

    def get_default_account_debit(self):
        return self.env.user.company_id.account_debit

    def get_default_account_credit(self):
        return self.env.user.company_id.account_credit

    def get_default_journal(self):
        return self.env.user.company_id.journal_id

    account_id = fields.Many2one('account.account', 'Account',  domain="[('deprecated', '=', False)]")
    voucher_ids = fields.Many2many('account.voucher', string="Receipts")
    project_salary_line_ids = fields.One2many('project.salary.line', 'project_labour_id')
    account_tax_id = fields.Many2one('account.tax', 'Tax', default=get_default_account_tax)
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)], default=get_default_account_debit)
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)], default=get_default_account_credit)
    journal_id = fields.Many2one('account.journal', string='Journal', states={'validated': [('readonly', True)]}, default=get_default_journal)
    move_ids = fields.Many2many('account.move', 'hr_custom_move_rel', 'hr_custom_id', 'move_id', string="Moves")
    name = fields.Char("Reference", copy=False, readonly=True, default=lambda x: _('New'))

    @api.multi
    def action_validate(self):
        if not self.journal_id:
            raise UserError(_('Journal is not set!! Please Set Journal.'))
        if not self.account_credit or not self.account_debit:
            raise UserError(_('You need to set debit/credit account for validate.'))

        debit_vals = {
            'name': self.analytical_account.name,
            'debit': self.total_labour_cost,
            'credit': 0.0,
            'account_id': self.account_debit.id,
        }
        credit_vals = {
            'name': self.analytical_account.name,
            'debit': 0.0,
            'credit': self.total_labour_cost,
            'account_id': self.account_credit.id,
        }
        vals = {
            'journal_id': self.journal_id.id,
            'date': datetime.now().date(),
            'ref': self.analytical_account.name,
            'state': 'draft',
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        move = self.env['account.move'].create(vals)
        move.action_post()
        self.write({'move_ids': [(4, move.id)]})
        return

    def submit_request(self):
        for rec in self:
            rec.action_validate()
            rec.write({'state': 'wait_approve'})

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.move_ids.ids)],
        }
    
    def compute_project_salary_line(self):
        payslip_ids = self.env['hr.payslip'].search([('account_analytical_id', '=', self.analytical_account.id)])
        if payslip_ids:
            salary_line_list = []
            total_gross_amount = 0.0
            for payslip in payslip_ids:
                gross_amount = sum(line.total for line in payslip.line_ids.filtered(lambda l: l.code == 'GROSS'))
                salary_line_list.append((0, 0, {'employee_id': payslip.employee_id.id,
                                                'date_from': payslip.date_from,
                                                'date_to': payslip.date_to,
                                                'struct_id': payslip.struct_id.id,
                                                'prelims_category_id': payslip.prelims_category_id.id,
                                                'gross_amount': gross_amount}))
                total_gross_amount += gross_amount
            
            self.project_salary_line_ids = salary_line_list
            self.total_labour_cost += total_gross_amount
        else:
            self.project_salary_line_ids = [(6, 0, [])]
        return
    
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.labor.seq') or _('New')
        res = super(ProjectLabour, self).create(vals)
        if res and res.type == 'daily':
            for line in res.daily_labour_cost:
                if line.trade:
                    line.trade.available_project_labour = True
        return res
    
    @api.multi
    def write(self, vals):
        res = super(ProjectLabour, self).write(vals)
        if res and self.type == 'daily':
            for line in self.daily_labour_cost:
                if line.trade:
                    line.trade.available_project_labour = True
        return res
                
    # def create_receipt(self):
    #     vals = {'account_id': self.account_id.id,
    #             'voucher_type': 'purchase',
    #             }
    #     voucher_id = self.env['account.voucher'].create(vals)
    #     self.voucher_ids = [(4, voucher_id.id)]
    
    # def action_view_receipts(self):
    #     if not self.voucher_ids:
    #         raise UserError(_("There is no Receipt for this Project Labour"))
    #     return {
    #             'name': _('Receipts'),
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'res_model': 'account.voucher',
    #             'type': 'ir.actions.act_window',
    #             'domain': [('id', 'in', self.voucher_ids.ids)],
    #             'context': {'default_voucher_type': 'purchase', 'voucher_type': 'purchase'},
    #         }


class ProjectLabourCost(models.Model):
    _inherit = 'project.labour.cost'
    
    trade = fields.Many2one('casual.workers', "Casual Worker")
    bank_name = fields.Char("Bank Name")
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        groups="hr.group_hr_user",
        help='Employee bank salary account')

    @api.onchange('trade')
    def onchange_casual_worker(self):
        self.bank_name = False
        self.bank_account_id = False
        if self.trade:
            self.bank_name = self.trade.bank_name or ''
            self.bank_account_id = self.trade.bank_account_id and self.trade.bank_account_id.id or False


class ProjectSalaryLine(models.Model):
    _name = "project.salary.line"
    
    project_labour_id = fields.Many2one('project.labour')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure')
    prelims_category_id = fields.Many2one('prelims.category', string="Project Stage")
    gross_amount = fields.Float("Gross Amount")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_default_payslip_journal(self):
        journal_id = self.env['account.journal'].search([('name', '=', 'General- HR')], limit=1)
        if journal_id:
            return journal_id
        else:
            return self.env['account.journal'].search([('type', '=', 'general')], limit=1)

    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]}, default=get_default_payslip_journal)
    