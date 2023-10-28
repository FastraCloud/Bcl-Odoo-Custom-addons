# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SubcontractorBlockWork(models.Model):
    _name = "subcontractor.block.work"
    _description = "Subcontractor Block Work"
    
    name = fields.Char('Name')
    analytical_account_id = fields.Many2one('account.analytic.account', string="Project")
    subcontractor = fields.Many2one('res.partner',"Sub Contractor")
    subcontract = fields.Char("Sub Contract")
    date = fields.Date('Date')
    bank_account = fields.Char("Bank Account")
    valuation_no = fields.Char("Valuation No")
    amount_due = fields.Float("Total Amount Due", compute="get_amount_due", store=True)
    total_amount_due = fields.Float("Total Amount Due", compute="get_total_amount_due", store=True)
    discount = fields.Float("WHT")
    discount_amount = fields.Float("WHT Amount", compute="get_total_amount_due", store=True)
    subcontractor_block_work_line_ids = fields.One2many('subcontractor.block.work.line', 'subcontractor_block_work_id', string="Block Work Lines")
    block_work_previous_payment_ids = fields.One2many('block.work.previous.payment', 'subcontractor_block_work_id', string="Previous Payment")
    previous_payment_amount = fields.Float('Previous Payment', compute='_get_previous_payment_amount', store=True)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('validate', 'Validate'), ('cancel', 'Cancel')], string="State", default='draft')
    
    @api.depends('subcontractor_block_work_line_ids.amount_due')
    def get_amount_due(self):
        for record in self:
            total = 0.0
            for line in self.subcontractor_block_work_line_ids:
                total += line.amount_due
            record.amount_due = total
        
    @api.depends('amount_due', 'discount', 'previous_payment_amount')
    def get_total_amount_due(self):
        for record in self:
            if record.discount == 0.0:
                record.total_amount_due = record.amount_due + record.previous_payment_amount
                record.discount_amount = -abs(0.0)
            else:
                record.discount_amount = -abs((record.amount_due * record.discount) / 100)
                record.total_amount_due = record.amount_due + record.discount_amount + record.previous_payment_amount
            
    
    @api.depends('block_work_previous_payment_ids.amount')
    def _get_previous_payment_amount(self):
        for record in self:
            total = 0.0
            for line in self.block_work_previous_payment_ids:
                total += line.amount
            record.previous_payment_amount = -abs(total)
            
    def submit(self):
        self.write({'state': 'submit'})
        
    def validate(self):
        self.write({'state': 'validate'})
        
    def cancel(self):
        self.write({'state': 'cancel'})
        
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('block.work') or _('New')
        return super(SubcontractorBlockWork, self).create(vals)
    
class SubcontractorBlockWorkLines(models.Model):
    _name = "subcontractor.block.work.line"

    def get_default_product(self):
        product_id = self.env['product.product'].search([('default_code', '=', 'SV0001')], limit=1)
        if product_id:
            return product_id.id
        return False
    
    subcontractor_block_work_id = fields.Many2one('subcontractor.block.work', string="Subcontractor Block Work")
    product_id = fields.Many2one('product.product', string='Product', ondelete='set null', default=get_default_product)
    account_id = fields.Many2one('account.account', string='Account', required=True, domain=[('deprecated', '=', False)],help="The income or expense account related to the selected product.")
    description = fields.Char("Description")
    qty_done = fields.Float('Quantity Done')
    unit_id = fields.Many2one('uom.uom',string="Unit")
    rate = fields.Float("Rate")
    amount = fields.Float("Amount", compute="get_amount")
    done = fields.Integer("%Done")
    amount_due = fields.Float("Amount Due", compute="get_amount")
    
    @api.depends('qty_done', 'rate', 'done')
    def get_amount(self):
        for record in self:
            record.amount = record.qty_done * record.rate
            record.amount_due = (record.done * record.amount) / 100
            
    
    @api.onchange('product_id')
    def _onchange_line_details(self):
        if not self.product_id:
            return
        account = self.product_id.product_tmpl_id.get_product_accounts()['expense']
        values = {
            'name': self.product_id.partner_ref,
            'account_id': account.id,
        }
        return {'value': values, 'domain': {}}
        
        
class BlockWorkLessPreviousPayment(models.Model):
    _name = "block.work.previous.payment"
    
    subcontractor_block_work_id = fields.Many2one('subcontractor.block.work', string="Subcontractor Block Work")
    name = fields.Char("Name")
    amount = fields.Float("Amount")
    
    