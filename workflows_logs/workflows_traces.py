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
    _description = "Traces of workflows of objects created by models"

    _columns = {
        'res_model_id': fields.many2one('ir.model', 'Object', required=True, help="Select object for which you want to generate log."),
        'state': fields.selection((("draft", "Draft"), ("subscribed", "Subscribed")), "Status", required=True)
        }

    _defaults = {
        'state': 'draft'
        }

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
                                wkf_act = self.pool.get('workflow.activity')                                
                                wkf_act_ids = wkf_act.search(cr, uid, [('wkf_id', '=', wkf_ids[0])], context=context)
                                if wkf_act_ids:
                                    wkf_workitems = self.pool.get('workflow.workitem')
                                    wkf_workitems_ids = wkf_workitems.search(cr, uid, [('act_id', 'in', wkf_act_ids)], context=context)
                                    if wkf_workitems_ids:
                                        wkf_logs = self.pool.get('wkf.logs')
                                        for workitem in wkf_workitems.browse(cr, uid, wkf_workitems_ids, context=context):
                                            wkf_log_data = dict()
                                            wkf_log_data['act_id'] = workitem.act_id.id
                                            wkf_log_data['user_id'] = uid
                                            wkf_log_data['res_id'] = workitem.inst_id.res_id
                                            wkf_log_data['wkf_trace_id'] = wkf_trace_id
                                            #wkf_log['timestamp'] =
                                            #wkf_log['res_state'] =
                                            #raise osv.except_osv('Test', wkf_log)
                                            wkf_logs.create(cr, SUPERUSER_ID, wkf_log_data, context=context)
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

workflows_traces()
