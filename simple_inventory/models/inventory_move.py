from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError

class InventoryMove(models.Model):
    _name = 'inventory.move'
    _description = 'Inventory Move'

    product_id = fields.Many2one('inventory.product',string='Itme',ondelete='restrict')
    move_type = fields.Selection([
        ('in','Stock In'),
        ('out','Stock Out'),
    ],string='Move Type',default='in')
    quantity = fields.Float('Quantity',default=1.0)
    date = fields.Date('Move Date',default=fields.Date.context_today)
    note = fields.Char('Note')
    product_code = fields.Char(related="product_id.code",string='Item Code',store=True,readonly=True)

    @api.onchange('product_id','move_type','quantity')
    def _onchange_move_available_stock(self):
        if self.move_type == 'out' and self.product_id and self.quantity > 0:
            if self.quantity > self.product_id.qty_on_hand:
                return {
                    'warning' : {
                        'title' : 'Stock unavailable',
                        'message' : (
                            f'{self.product_id.name} stock'
                            f'{self.product_id.qty_on_hand} '
                        )
                    }
                }

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError('Quantity cannot be negative')

    @api.constrains('move_type','quantity','product_id')
    def _check_stock_out_not_negative(self):
        for rec in self:
            if rec.move_type != 'out':
                continue

            other_moves = self.env['inventory.move'].search([
                ('product_id','=',rec.product_id.id),
                ('id','!=',rec.id),
            ])

            in_qty = sum(other_moves.filtered(lambda m : m.move_type == 'in').mapped('quantity'))
            out_qty = sum(other_moves.filtered(lambda m : m.move_type == 'out').mapped('quantity'))
            current_stock = in_qty - out_qty

            if rec.quantity > current_stock:
                raise ValidationError(
                    f'"{rec.product_id.name}" အတွက် လက်ကျန် {current_stock} '
                    f'ခုသာ ရှိပါသည်။ {rec.quantity} ခု ထုတ်၍မရပါ။'
                )

    def action_duplicate_as_in(self):
        self.ensure_one()
        if self.move_type != 'out':
            raise UserError('"Stock Out" move ကိုသာ "duplicate as in" လုပ်နိုင်ပါသည်။')


        new_move = self.create({
            'prodcut_id' : self.product_id.id,
            'move_type' : 'in',
            'quantity' : self.quantity,
            'note' : f'Returned from move #{self.id}',
        })
        return new_move