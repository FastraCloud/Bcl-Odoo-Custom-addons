# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class IronBender(models.Model):
    _name = "iron.bender"
    _description = "Iron Bender"
    
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
    iron_bender_line_ids = fields.One2many('iron.bender.line', 'iron_bender_id', string="Lines")
    iron_bender_previous_payment_ids = fields.One2many('iron.bender.previous.payment', 'iron_bender_id', string="Previous Payment")
    previous_payment_amount = fields.Float('Previous Payment', compute='_get_previous_payment_amount', store=True)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('validate', 'Validate'), ('cancel', 'Cancel')], string="State", default='draft')
    
    @api.depends('iron_bender_line_ids.amount_due')
    def get_amount_due(self):
        for record in self:
            total = 0.0
            for line in self.iron_bender_line_ids:
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
            
    
    @api.depends('iron_bender_previous_payment_ids.amount')
    def _get_previous_payment_amount(self):
        for record in self:
            total = 0.0
            for line in self.iron_bender_previous_payment_ids:
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
            vals['name'] = self.env['ir.sequence'].next_by_code('iron.bender') or _('New')
        return super(IronBender, self).create(vals)
    
class IronBenderLines(models.Model):
    _name = "iron.bender.line"
    
    def get_default_product(self):
        product_id = self.env['product.product'].search([('default_code', '=', 'SV0001')], limit=1)
        if product_id:
            return product_id.id
        return False
    
    iron_bender_id = fields.Many2one('iron.bender', string="Iron Bender")
    product_id = fields.Many2one('product.product', string='Product', ondelete='set null', default=get_default_product)
    account_id = fields.Many2one('account.account', string='Account', required=True, domain=[('deprecated', '=', False)],help="The income or expense account related to the selected product.")
    description = fields.Char("Description")
    iron_bender_reinforcement_size_ids = fields.One2many('iron.bender.reinforcement.size', 'iron_bender_line_id')
    qty_done = fields.Float('Total Quantity', compute="get_toal_qty_done", store= True)
    unit_id = fields.Many2one('uom.uom',string="Unit")
    rate = fields.Float("Rate")
    amount = fields.Float("Amount", compute="get_amount")
    done = fields.Integer("%Done")
    amount_due = fields.Float("Amount Due", compute="get_amount")
    
    @api.depends('iron_bender_reinforcement_size_ids.qty')
    def get_toal_qty_done(self):
        for rec in self:
            qty_done = 0.0
            for size_id in rec.iron_bender_reinforcement_size_ids:
                qty_done += size_id.qty
            rec.qty_done = qty_done
    
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
        
class IronBenderPreviousPayment(models.Model):
    _name = "iron.bender.previous.payment"
    
    iron_bender_id = fields.Many2one('iron.bender', string="Iron Bender")
    name = fields.Char("Name")
    amount = fields.Float("Amount")
    
class IronBenderReinforcementSize(models.Model):
    _name = "iron.bender.reinforcement.size"
    
    iron_bender_line_id = fields.Many2one('iron.bender.line', string="Iron Bender Line")
    reinforcement_bar_size = fields.Many2one('reinforcement.bar.size',string="Reinforcement Size")
    qty = fields.Float("Quantity")
    
class ReinforcementBarSize(models.Model):
    _name = "reinforcement.bar.size"
    
    name = fields.Char("Size")
    