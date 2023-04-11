from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LandedCostApproveWizard(models.TransientModel):
    _name = 'landed.cost.approve.wizard'
    _description = 'Landed Cost Approval Wizard'

    @api.model
    def default_get(self, fields):
        """
        Default Get
        :param fields:
        :return:
        """
        res = super(LandedCostApproveWizard, self).default_get(fields)
        stock_landed_cost_id = self.env['stock.landed.cost'].browse(self.env.context.get('active_id'))
        if stock_landed_cost_id:
            res['stock_landed_cost_id'] = stock_landed_cost_id.id
        return res

    stock_landed_cost_id = fields.Many2one('stock.landed.cost', string='Landed Cost ID')
    approve_by_id = fields.Many2one('res.users', string='Approve By')

    @api.onchange('stock_landed_cost_id')
    def onchange_stock_landed_cost_id(self):
        """
        Onchange Landed Cost Id
        :return:
        """
        if self.stock_landed_cost_id:
            user_approved_ids = []
            approval_user = self.env['res.users'].search([])
            for rec in approval_user:
                if rec.has_group('landed_cost_addons.group_landed_cost_approval'):
                    user_approved_ids.append(rec.id)
            return {'domain': {'approve_by_id': [('id', 'in', user_approved_ids)]}}

    def approve_landed_cost(self):
        """
        Approve Landed Cost
        :return:
        """
        if self.approve_by_id:
            if self.stock_landed_cost_id.state != 'draft':
                raise UserError(_('Document has been Processed Already.!!!'))
            self.stock_landed_cost_id.approve_by_id = self.approve_by_id.id
            self.stock_landed_cost_id.state = 'waiting_approval'
            if self.env.company.is_allow_email:
                template_id = self.env.ref('nuro_landed_cost_addons.landed_cost_approval_email')
                if template_id:
                    action_id = self.env.ref('stock_landed_costs.action_stock_landed_cost').id
                    params = "/web#id=%s&view_type=form&model=stock.landed.cost&action=%s" % (
                        self.stock_landed_cost_id.id, action_id)
                    current_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    landed_url = str(current_url) + str(params)
                    template_id['email_to'] = self.approve_by_id.email
                    template_id['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    try:
                        template_id.body_html = template_id.body_html.replace('landed_url', landed_url)
                        template_id.send_mail(self.stock_landed_cost_id.id, force_send=True)
                        template_id.body_html = template_id.body_html.replace(landed_url, 'landed_url')
                    except Exception:
                        pass
            # comment but need to take without asset module because landed_type field
            # in asset module need to fix
            # if self.stock_landed_cost_id.landed_type == 'asset':
            #     self.stock_landed_cost_id.compute_cost_lines_po()