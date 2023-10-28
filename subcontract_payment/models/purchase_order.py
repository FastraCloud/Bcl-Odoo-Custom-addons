from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_subcontractor_purchase = fields.Boolean()

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        res = super(PurchaseOrder, self)._get_destination_location()
        if self.is_subcontractor_purchase:
            res = self.picking_type_id.default_location_dest_id.id
        return res

    @api.model
    def create(self, vals):
        if self.env.context.get('default_is_subcontractor_purchase', False) and vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('subcontractor.purchase') or '/'
        return super(PurchaseOrder, self).create(vals)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_subcontractor_purchase_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        purchase_order_groups = self.env['purchase.order'].read_group(
            domain=[('is_subcontractor_purchase', '=', True), ('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in purchase_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.subcontractor_purchase_order_count += group['partner_id_count']
                partner = partner.parent_id

    @api.multi
    def _compute_subcontractor_supplier_invoice_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([('id', 'child_of', self.ids)])
        subcontractor_partner_ids = all_partners.filtered(lambda partner: partner.is_subcontractor)
        subcontractor_partner_ids.read(['parent_id'])

        supplier_invoice_groups = self.env['account.invoice'].read_group(
            domain=[('partner_id', 'in', subcontractor_partner_ids.ids),
                    ('type', 'in', ['in_invoice', 'in_refund'])],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in supplier_invoice_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.subcontractor_supplier_invoice_count += group['partner_id_count']
                partner = partner.parent_id

    is_subcontractor = fields.Boolean()
    subcontractor_purchase_order_count = fields.Integer(compute='_compute_subcontractor_purchase_order_count', string='Subcontractor Purchase Order Count')
    subcontractor_supplier_invoice_count = fields.Integer(compute='_compute_subcontractor_supplier_invoice_count', string='# Subcontractor Vendor Bills')
    tin = fields.Char('TIN')