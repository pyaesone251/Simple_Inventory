from odoo import models,fields,api
from odoo.exceptions import ValidationError

class InventoryProduct(models.Model):
    _name = 'inventory.product'
    _description = 'Inventory Product'

    name = fields.Char('Item Name')
    code = fields.Char('Item Code')
    unit_price = fields.Float('Unit Price',default=0.0)
    move_ids = fields.One2many('inventory.move','product_id',string='Stock Moves')
    qty_on_hand = fields.Float('Qty On Hand',compute='_compute_qty_on_hand',store=True)

    @api.depends('move_ids.quantity','move_ids.move_type')
    def _compute_qty_on_hand(self):
        for rec in self:
            in_moves = rec.move_ids.filtered(lambda m: m.move_type == 'in')
            out_moves = rec.move_ids.filtered(lambda m: m.move_type == 'out')

            total_in = sum(in_moves.mapped('quantity'))
            total_out = sum(out_moves.mapped('quantity'))

            rec.qty_on_hand = total_in - total_out

    _sql_constraints = [
        ('code_unique','UNIQUE(code)','Item Code must be unique')
    ]

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for rec in self:
            if rec.unit_price < 0:
                raise ValidationError('Unit Price cannot be negative')
    