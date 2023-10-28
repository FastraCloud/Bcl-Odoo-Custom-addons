# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    is_subcontract_bill_payment = fields.Boolean(string='Subcontract Bill Payment', compute="get_subcontractor_bill_payment", store=True)
    
    @api.multi
    @api.depends('invoice_ids', 'invoice_ids.is_subcontractor_bill')
    def get_subcontractor_bill_payment(self):
        for rec in self:
            for invoice in rec.invoice_ids:
                if invoice.is_subcontractor_bill:
                    rec.is_subcontract_bill_payment = True