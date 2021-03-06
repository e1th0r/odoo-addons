# -*- encoding: utf-8 -*-
################################################################################
#
#    This software has been developed and funded by 
#    ASOCIACION COOPERATIVA HOATZIN DE BASE TECNOLOGICA, R.L.
#    Copyright (C) 2015  HOATZIN 
#    Manuel Márquez <mmarquez@hoatzin.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _

class workflows_traces(osv.Model):
    """
    Traces of workflows of objects created by models
    """
    _name = "wkf.traces"
    _rec_name = "res_model_name"
    _description = "Traces of workflows of objects created by models"

    _columns = {
        'res_model_id': fields.many2one('ir.model', 'Object', required=True, help="Select object for which you want to generate log."),
        'state': fields.selection((("draft", "Draft"), ("subscribed", "Subscribed")), "Status", required=True),
        'res_model_name': fields.related(
            'res_model_id', 
            'name', 
            string='Object name', 
            type='char', 
            select=True,
            ),
        }

    _defaults = {
        'state': 'draft'
        }

    _sql_constraints = [
        ('res_model_uniq', 'UNIQUE (res_model_id)', _('There is already a trace for this model!')),
        ]

    def _process_logs(self, cr, uid, context=None, **kwargs):
        wkf_ids = kwargs['wkf_ids']
        wkf_trace_id = kwargs.get('wkf_trace_id')
        res_model_id = kwargs['res_model_id']
        wkf_act = self.pool.get('workflow.activity')                                
        wkf_act_ids = wkf_act.search(cr, uid, [('wkf_id', '=', wkf_ids[0])], context=context)
            
        if wkf_act_ids:
            wkf_workitems = self.pool.get('workflow.workitem')
            wkf_workitems_ids = wkf_workitems.search(cr, uid, [('act_id', 'in', wkf_act_ids)], context=context)

            if wkf_workitems_ids:
                wkf_logs = self.pool.get('wkf.logs')

                for workitem in wkf_workitems.browse(cr, uid, wkf_workitems_ids, context=context):
                        search_args = list()
                        search_args.append(('res_model_id', '=', res_model_id))
                        search_args.append(('res_id', '=', workitem.inst_id.res_id))
                        search_args.append(('act_id', '=', workitem.act_id.id))
                        log_exists = wkf_logs.search(cr, SUPERUSER_ID, search_args, context=context)
                        if not log_exists:
                            wkf_log_data = dict()
                            wkf_log_data['act_id'] = workitem.act_id.id
                            wkf_log_data['user_id'] = SUPERUSER_ID
                            wkf_log_data['res_id'] = workitem.inst_id.res_id
                            wkf_log_data['wkf_trace_id'] = wkf_trace_id
                            wkf_log_data['on_subscribe_trace'] = True
                            wkf_logs.create(cr, SUPERUSER_ID, wkf_log_data, context=context)
                return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('state'):
            if vals['state'] == 'subscribed':
                ir_model = self.pool.get('ir.model')
                model_exist = ir_model.read(cr, uid, vals['res_model_id'], ['model'], context=context)
                if model_exist:
                    wkf = self.pool.get('workflow')
                    wkf_ids = wkf.search(cr, uid, [('osv', '=', model_exist['model'])], context=context)
                    if wkf_ids:
                        if len(wkf_ids) == 1:
                            wkf_trace_id = super(workflows_traces, self).create(cr, uid, vals, context)
                            if wkf_trace_id:
                                kwargs = dict()
                                kwargs['wkf_ids'] = wkf_ids
                                kwargs['wkf_trace_id'] = wkf_trace_id
                                kwargs['res_model_id'] = vals['res_model_id']
                                if self._process_logs(cr, uid, **kwargs):
                                    cr.commit()
                                    return wkf_trace_id
                        else:
                            raise osv.except_osv(_('Warning'), _("For now it is not supported track more than one workflow by model."))
                    else:
                        raise osv.except_osv(_('Error'), _("There isn't a workflow for this model!"))
                else:
                    raise osv.except_osv(_('Error'), _("The model doesn't exist!"))
            else:
                wkf_trace_id = super(workflows_traces, self).create(cr, uid, vals, context)
                return wkf_trace_id
        else:
            wkf_trace_id = super(workflows_traces, self).create(cr, uid, vals, context)
            return wkf_trace_id

    def write(self, cr, uid, ids, vals, context=None):
        write_result = super(workflows_traces, self).write(cr, uid, ids, vals, context=context)        
        if write_result and vals.get('state', False):
            if vals.get('state') == 'subscribed':
                ir_model = self.pool.get('ir.model')
                wkf = self.pool.get('workflow')
                for wkf_trace_id in ids:
                    wkf_trace = self.browse(cr, uid, wkf_trace_id, context=context)
                    wkf_trace_model = ir_model.read(cr, uid, wkf_trace.res_model_id.id, ['model'], context=context)
                    wkf_ids = wkf.search(cr, uid, [('osv', '=', wkf_trace_model['model'])], context=context)
                    kwargs = dict()
                    kwargs['wkf_ids'] = wkf_ids
                    kwargs['wkf_trace_id'] = wkf_trace_id
                    kwargs['res_model_id'] = wkf_trace.res_model_id.id
                    self._process_logs(cr, uid, **kwargs)
                cr.commit()
            return write_result

workflows_traces()
