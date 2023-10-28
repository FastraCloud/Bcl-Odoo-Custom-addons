# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"
    
    is_subcontract_payment = fields.Boolean(string='Subcontract Payment')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    element = fields.Many2one('project.element', String="Element")
    category = fields.Many2one('project.element.category', string='Category')
    subcategory_id = fields.Many2one('subcategory.subcategory', string='Subcategory')
    prelims_category_id = fields.Many2one('prelims.category', string="Cost Code")

    @api.multi
    @api.onchange('prelims_category_id')
    def onchange_prelims_category_id(self):
        for rec in self:
            cost_code_dictionary_id = self.env['cost.code.dictionary'].search([('prelims_category_id', '=', rec.prelims_category_id.id)], order="id desc", limit=1)
            if cost_code_dictionary_id:
                rec.update({'element': cost_code_dictionary_id.project_element_id and cost_code_dictionary_id.project_element_id.id or False,
                            'category': cost_code_dictionary_id.project_element_category_id and cost_code_dictionary_id.project_element_category_id.id or False,
                            'subcategory_id': cost_code_dictionary_id.subcategory_id and cost_code_dictionary_id.subcategory_id.id or False
                            })
            else:
                rec.update({'element': False,
                            'category': False,
                            'subcategory_id': False
                            })


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    account_analytic_id = fields.Many2one('account.analytic.account', string='Project')
    is_subcontractor_bill = fields.Boolean(string='Subcontract Bill')
    subcontractor_bill_type = fields.Selection([('block_word',' Block Work'),
                                                ('iron_bender',' Iron Bender')], string="Type")
    block_work_id = fields.Many2one('subcontractor.block.work', string="Block Work")
    iron_bender_id = fields.Many2one('iron.bender', string="Iron Bender")
    subcontractor_purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Add Subcontractor Purchase Order'
    )

    @api.onchange('subcontractor_purchase_id')
    def _onchange_subcontractor_purchase_order(self):
        if not self.subcontractor_purchase_id:
            return {}
        self.currency_id = self.subcontractor_purchase_id.currency_id
        new_lines = self.env['account.invoice.line']
        for line in self.subcontractor_purchase_id.order_line:
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line
        self.invoice_line_ids += new_lines
        self.payment_term_id = self.subcontractor_purchase_id.payment_term_id
        self.subcontractor_purchase_id = False
        return {}
    
    @api.multi
    @api.onchange('subcontractor_bill_type')
    def onchange_subcontractor_bill_type(self):
        self.block_work_id = False
        self.iron_bender_id = False
    
    @api.multi
    @api.onchange('block_work_id')
    def _onchange_block_work_id(self):
        if not self.block_work_id:
            return
        line_list = []
        for bw_line in self.block_work_id.subcontractor_block_work_line_ids:
            line_list.append((0, 0, {'product_id': bw_line.product_id.id or False,
                                     'name': bw_line.description,
                                     'account_id': bw_line.account_id.id,
                                     'account_analytic_id': self.block_work_id.analytical_account_id and self.block_work_id.analytical_account_id.id or False,
                                     'quantity': bw_line.qty_done,
                                     'price_unit': bw_line.rate}))
        values = {
            'invoice_line_ids': line_list,
            'partner_id': self.block_work_id.subcontractor and self.block_work_id.subcontractor.id or False,
        }
        return {'value': values, 'domain': {}}
    
    @api.multi
    @api.onchange('iron_bender_id')
    def _onchange_iron_bender_id(self):
        if not self.iron_bender_id:
            return
        line_list = []
        for ib_line in self.iron_bender_id.iron_bender_line_ids:
            line_list.append((0, 0, {'product_id': ib_line.product_id.id or False,
                                     'name': ib_line.description,
                                     'account_id': ib_line.account_id.id,
                                     'account_analytic_id': self.iron_bender_id.analytical_account_id and self.iron_bender_id.analytical_account_id.id or False,
                                     'quantity': ib_line.qty_done,
                                     'price_unit': ib_line.rate,
                                     }))
        values = {
            'invoice_line_ids': line_list,
            'partner_id': self.iron_bender_id.subcontractor and self.iron_bender_id.subcontractor.id or False,
        }
        return {'value': values, 'domain': {}}

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        project_cost_obj = self.env['project_cost.project_cost'].sudo()
        for line in self.invoice_line_ids:
            project_cost_id = project_cost_obj.search([('analytical_account', '=', line.account_analytic_id.id)],
                                                      order="id desc", limit=1)
            if project_cost_id:
                cost_tracking_id = project_cost_id.cost_tracking_ids.filtered(
                    lambda ct: ct.prelims_category_id.id == line.prelims_category_id.id)
                if cost_tracking_id:
                    cost_tracking_id.write({'actual_subcontractor_amount': cost_tracking_id.actual_subcontractor_amount + line.price_subtotal})
                else:
                    project_cost_id.write({'cost_tracking_ids': [(0, 0, {
                                                                     'actual_subcontractor_amount': line.price_subtotal,
                                                                     'prelims_category_id': line.prelims_category_id and line.prelims_category_id.id or False,
                                                                     'category': line.category and line.category.id or False,
                                                                     'subcategory_id': line.subcategory_id and line.subcategory_id.id or False,
                                                                     'element': line.element and line.element.id or False,
                                                                     })]})
        return res