# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectCost(models.Model):
    _inherit = "project_cost.project_cost"

    # project_labor_actual_ids = fields.Many2many('project.labour', compute="get_project_labour_data")
    # material_actual_ids = fields.Many2many('account.move', compute="get_material_data")
    # other_material_actual_ids = fields.Many2many('account.move', compute="get_other_material_data")
    # subcontractor_bill_actual_ids = fields.Many2many('account.invoice', 'project_cost_bill_rel', compute="get_subcontractor_data")
    # subcontractor_bill_iron_bender_work_actual_ids = fields.Many2many('account.invoice', 'project_cost_bill_iron_rel', compute="get_subcontractor_data")
    
    # @api.depends('analytical_account')
    # def get_project_labour_data(self):
    #     for rec in self:
    #         rec.project_labor_actual_ids = [(6, 0, [])]
    #         labour_list = []
    #         for labour_id in self.env['project.labour'].search([('state', '=', 'Approve'),('analytical_account', '=', rec.analytical_account.id)]):
    #             labour_list.append(labour_id.id)
    #         rec.project_labor_actual_ids = [(6, 0, labour_list)]

    # @api.depends('analytical_account')
    # def get_material_data(self):
    #     for rec in self:
    #         rec.material_actual_ids = [(6, 0, [])]
    #         material_list = []
    #         inventory_list = []
    #         for stock_inventory_line_id in self.env['stock.inventory.line'].search([('inventory_id.state', '=', 'done'),
    #                                                                   ('analytical_account', '=', rec.analytical_account.id)]):
    #             inventory_list.append(stock_inventory_line_id.inventory_id.id)
    #
    #         for inventory in inventory_list:
    #             for account_move in self.env['account.move'].search([('picking_id', '=', inventory), ('consumption', '=', True), ('picking_id.type', '=','consumption')]):
    #                 if ': Return' in account_move.ref:
    #                     continue
    #                 else:
    #                     material_list.append(account_move.id)
    #         rec.material_actual_ids = [(6, 0, material_list)]

    # @api.depends('analytical_account')
    # def get_other_material_data(self):
    #     for rec in self:
    #         rec.other_material_actual_ids = [(6, 0, [])]
    #         material_list = []
    #         inventory_list = []
    #         for stock_inventory_line_id in self.env['stock.inventory.line'].search([('inventory_id.state', '=', 'done'),
    #                                                                                 ('analytical_account', '=',
    #                                                                                  rec.analytical_account.id)]):
    #             inventory_list.append(stock_inventory_line_id.inventory_id.id)
    #
    #         for inventory in inventory_list:
    #             for account_move in self.env['account.move'].search(
    #                     [('picking_id', '=', inventory), ('consumption', '=', True), ('picking_id.type','=', 'other_consumption')]):
    #                 if ': Return' in account_move.ref:
    #                     continue
    #                 else:
    #                     material_list.append(account_move.id)
    #         rec.other_material_actual_ids = [(6, 0, material_list)]
    
    # @api.depends('analytical_account')
    # def get_subcontractor_data(self):
    #     for rec in self:
    #         rec.subcontractor_bill_actual_ids = [(6, 0, [])]
    #         bill_list = []
    #         for invoice_line_id in self.env['account.invoice.line'].search([('invoice_id.is_subcontractor_bill', '=', True),
    #                                                                   ('invoice_id.state', 'not in', ['draft', 'cancel']),
    #                                                                   ('account_analytic_id', '=', rec.analytical_account.id)]):
    #
    #             bill_list.append(invoice_line_id.invoice_id.id)
    #         rec.subcontractor_bill_actual_ids = [(6, 0, bill_list)]
            
