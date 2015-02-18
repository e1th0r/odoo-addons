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

from openerp.workflow import workitem
from openerp.workflow.wkf_logs import log
from openerp import pooler, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

def create(cr, act_datas, inst_id, ident, stack):
    for act in act_datas:
        cr.execute("select nextval('wkf_workitem_id_seq')")
        id_new = cr.fetchone()[0]
        cr.execute("insert into wkf_workitem (id,act_id,inst_id,state) values (%s,%s,%s,'active')", (id_new, act['id'], inst_id))
        cr.execute('select * from wkf_workitem where id=%s',(id_new,))
        res = cr.dictfetchone()
        log(cr,ident,act['id'],'active')
        result_process = workitem.process(cr, res, ident, stack=stack)
        if result_process:
            pool_obj = pooler.get_pool(cr.dbname)
            wkf_traces = pool_obj.get('wkf.traces')
            wkf_traces_subscribed_ids = wkf_traces.search(cr, SUPERUSER_ID, [('state', '=', 'subscribed')])
            if wkf_traces_subscribed_ids:
                wkf_activity = pool_obj.get('workflow.activity')
                workitem_activity = wkf_activity.browse(cr, SUPERUSER_ID, res['act_id'])
                model_name = workitem_activity.wkf_id.osv
                ir_model = pool_obj.get('ir.model')
                model_id = ir_model.search(cr, SUPERUSER_ID, [('model', '=', model_name)])[0]
                for wkf_trace in wkf_traces.browse(cr, SUPERUSER_ID, wkf_traces_subscribed_ids):
                    if wkf_trace.res_model_id.id == model_id:
                        wkf_logs = pool_obj.get('wkf.logs')
                        wkf_log_data = dict()
                        wkf_log_data['act_id'] = res['act_id']
                        wkf_log_data['user_id'] = int(ident[0])
                        wkf_log_data['res_id'] = int(ident[2])
                        wkf_log_data['wkf_trace_id'] = wkf_trace.id
                        wkf_log_id = wkf_logs.create(cr, SUPERUSER_ID, wkf_log_data)
                        _logger.info("WORKFLOWS LOGS TEEEEEEEEEEEEEEEST %s", str(wkf_log_id))

workitem.create = create
