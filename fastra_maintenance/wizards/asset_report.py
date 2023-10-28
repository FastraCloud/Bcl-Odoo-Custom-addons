from odoo import fields, models, _
from odoo.exceptions import UserError
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64
from io import BytesIO


class AssetReport(models.TransientModel):
    _name = 'asset.report'
    _description = 'Asset Report'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    type = fields.Selection([('project', 'Project'), ('asset', 'Asset')], string='Type', default='project')
    project_ids = fields.Many2many('account.analytic.account', string='Project')
    asset_registration_ids = fields.Many2many('fastra.asset.registration', string='Asset')
    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('File Name')

    def get_movement_data(self):
        movement_ids = self.env['asset.movement'].search([('project_id', 'in', self.project_ids.ids),
                                           ('create_date', '>=', self.from_date),
                                           ('create_date', '<=', self.to_date)])
        return movement_ids

    def get_asset_data(self):
        return self.env['register.asset.maintenance.cost'].search([('asset_registration_id', 'in', self.asset_registration_ids.ids)])

    def print_pdf(self):
        if self.type == 'project':
            if not self.from_date or not self.to_date:
                raise UserError(_('You need to date first!'))
            if not self.project_ids:
                raise UserError(_('Please select Project!'))
            movement_ids = self.get_movement_data()
            if not movement_ids:
                raise UserError(_('No data found for this project during this period!'))
        else:
            asset_ids = self.get_asset_data()
            if not asset_ids:
                raise UserError(_('No data found for this assets!'))
        return self.env.ref('fastra_maintenance.report_asset_maintenance').report_action(self)

    def print_excel(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)

        worksheet = workbook.add_worksheet('Asset Report')

        bold = workbook.add_format({'bold': True})
        border = workbook.add_format({'border': 1})
        format1 = workbook.add_format({'bold': True, 'border': 1})

        if self.type == 'project':
            if not self.from_date or not self.to_date:
                raise UserError(_('You need to date first!'))
            if not self.project_ids:
                raise UserError(_('Please select Project!'))
            row = 0
            worksheet.write(row, 0, 'Code', format1)
            worksheet.write(row, 1, 'Asset', format1)
            worksheet.write(row, 2, 'Hire cost/day', format1)
            worksheet.write(row, 3, 'Project', format1)
            worksheet.write(row, 4, 'Collection Date', format1)
            worksheet.write(row, 5, 'Return Date', format1)
            worksheet.write(row, 6, 'Request By', format1)
            worksheet.write(row, 7, 'No of Days', format1)
            worksheet.write(row, 8, 'Amount Charged', format1)

            movement_ids = self.get_movement_data()
            if not movement_ids:
                raise UserError(_('No data found for this project during this period!'))
            row += 1
            for line in movement_ids:
                worksheet.write(row, 0, line.asset_registration_id and line.asset_registration_id.code or '')
                worksheet.write(row, 1, line.name or '')
                worksheet.write(row, 2, line.hire_cost or '')
                worksheet.write(row, 3, line.project_id and line.project_id.name or '')
                worksheet.write(row, 4, line.collection_date and line.collection_date.strftime('%m/%d/%Y') or '')
                worksheet.write(row, 5, line.return_date and line.return_date.strftime('%m/%d/%Y') or '')
                worksheet.write(row, 6, line.request_by or '')
                worksheet.write(row, 7, line.no_of_days or '')
                worksheet.write(row, 8, line.amount_charged or '')
                row += 1

            workbook.close()
            file_data.seek(0)
            self.write(
                {'excel_file': base64.encodebytes(file_data.read()),
                 'file_name': 'Asset Project Report.xlsx'})

            self.ensure_one()
            return {
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=asset.report&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
                'target': 'current'
            }
        else:
            row = 0
            worksheet.write(row, 0, 'Code', format1)
            worksheet.write(row, 1, 'Asset', format1)
            worksheet.write(row, 2, 'Asset Code', format1)
            worksheet.write(row, 3, 'Hire cost/day', format1)
            worksheet.write(row, 4, 'Maintenance Cost', format1)
            worksheet.write(row, 5, 'Replacement of Parts', format1)
            worksheet.write(row, 6, 'Operator', format1)
            worksheet.write(row, 7, 'Fuel', format1)
            worksheet.write(row, 8, 'Total Dep Cost', format1)

            asset_ids = self.get_asset_data()
            if not asset_ids:
                raise UserError(_('No data found for this assets!'))
            row += 1
            for line in asset_ids:
                worksheet.write(row, 0, line.asset_registration_id and line.asset_registration_id.code or '')
                worksheet.write(row, 1, line.name or '')
                worksheet.write(row, 2, line.asset_code or '')
                worksheet.write(row, 3, line.hire_cost or '')
                worksheet.write(row, 4, line.maintenance_cost or '')
                worksheet.write(row, 5, line.replacement_of_parts or '')
                worksheet.write(row, 6, line.operator or '')
                worksheet.write(row, 7, line.fuel or '')
                worksheet.write(row, 8, line.total_dep_cost or '')
                row += 1

            workbook.close()
            file_data.seek(0)
            self.write(
                {'excel_file': base64.encodebytes(file_data.read()),
                 'file_name': 'Asset Report.xlsx'})

            self.ensure_one()
            return {
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=asset.report&id=" + str(self.id) + "&filename_field=filename&field=excel_file&download=true&filename=" + self.file_name,
                'target': 'current'
            }


