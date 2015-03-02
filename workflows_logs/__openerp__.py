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

{
    'name' : 'Logs of Workflows of Objects',
    'version': '0.1',
    'author': u'Asociación Cooperativa Hoatzin de Base Tecnológica R.L.',
    'website': 'hoatzin.org',
    'description':
        u"""
        Logs of Workflows
        """,
    'depends': [
        'base'
    ],
    'data': [
        'security/workflows_logs_security.xml',
        'security/ir.model.access.csv',
        'workflows_logs_workflow.xml',
        'workflows_traces_view.xml',
        'workflows_logs_view.xml'
    ],
    'demo': [
        ],
    'test': [
     ],
    'auto_install': False,
    'installable': True,
    'images': [
    ],
}
