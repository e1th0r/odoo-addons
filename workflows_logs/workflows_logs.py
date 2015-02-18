# -*- encoding: utf-8 -*-
################################################################################
#
#    This software has been developed and funded by 
#    ASOCIACION COOPERATIVA HOATZIN DE BASE TECNOLOGICA, R.L.
#    Copyright (C) 2015  HOATZIN 
#    Manuel Márquez <mmarquez@hoatzin.org>,
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

from openerp.osv import osv, fields
import time

class workflows_logs(osv.Model):
    """
    Logs of workflows of objects created by models
    """
    _name = 'wkf.logs'
    _table = 'workflows_logs'
    _description = "Logs of workflows of objects created by models"

    def _get_res_name(self, cr, uid, ids, *args):
        data = {}
        for resname in self.browse(cr, uid, ids,[]):
            model_object = resname.wkf_trace_id.res_model_id
            res_id = resname.res_id
            if model_object and res_id:
                model_pool = self.pool.get(model_object.model)
                res = model_pool.read(cr, uid, res_id, ['name'])
                if res:
                    data[resname.id] = res['name']
                else:
                    data[resname.id] = False                    
            else:
                 data[resname.id] = False
        return data

    def _get_res_state(self, cr, uid, ids, field_name, arg, context=None): 
        data = {}
        for wkf_log in self.browse(cr, uid, ids, context=context):
            model_object = wkf_log.wkf_trace_id.res_model_id
            res_id = wkf_log.res_id
            if model_object and res_id:
                model_pool = self.pool.get(model_object.model)
                res = model_pool.read(cr, uid, res_id, ['state'], context=context)
                if res:
                    data[wkf_log.id] = res['state']
                else:
                    data[wkf_log.id] = False                    
            else:
                 data[wkf_log.id] = False
        return data


    _columns = {
        "res_id": fields.integer('Resource Id', required=True, select=1),
        "user_id": fields.many2one('res.users', 'User', required=True, select=1),
        "act_id": fields.many2one('workflow.activity', 'Activity', required=True, select=1),
        "timestamp": fields.datetime("Date", required=True, select=True),
        "wkf_trace_id": fields.many2one('wkf.traces', 'Traces of workflow', required=True, select=1, ondelete="restrict"),
        'res_state': fields.function(
            _get_res_state, 
            method=True, 
            string='Resource State', 
            type='char',
            ),
        'res_name': fields.function(
            _get_res_name, 
            method=True, 
            string='Resource Name', 
            type='char',
            )
        }

    _defaults = {
        "timestamp": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }

    _order = "timestamp desc"

workflows_logs()
