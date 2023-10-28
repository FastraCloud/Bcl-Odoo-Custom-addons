# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountVoucher(models.Model):
    _inherit = "account.voucher"
    
    project_stage_id = fields.Many2one('prelims.category', string="Cost Code")
    analytical_account_id = fields.Many2one('account.analytic.account', string="Project")
    block_work_id = fields.Many2one('subcontractor.block.work', string="Block Work")
    iron_bender_id = fields.Many2one('iron.bender', string="Iron Bender")
    
    @api.multi
    def subcontractor_proforma_voucher(self):
        self.action_move_line_create()
        if self.move_id:
            self.move_id.write({'is_subcontract_payment':True})
            
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
                                     'quantity': bw_line.qty_done,
                                     'price_unit': bw_line.rate}))
        values = {
            'line_ids': line_list,
            'partner_id': self.block_work_id.subcontractor and self.block_work_id.subcontractor.id or False,
            'analytical_account_id': self.block_work_id.analytical_account_id and self.block_work_id.analytical_account_id.id or False,
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
                                     'quantity': ib_line.qty_done,
                                     'price_unit': ib_line.rate,
                                     }))
        values = {
            'line_ids': line_list,
            'partner_id': self.iron_bender_id.subcontractor and self.iron_bender_id.subcontractor.id or False,
            'analytical_account_id': self.iron_bender_id.analytical_account_id and self.iron_bender_id.analytical_account_id.id or False,
        }
        return {'value': values, 'domain': {}}
