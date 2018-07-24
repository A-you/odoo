# OdooLightWorkflow, a lightweight workflow engine for Odoo
# Copyright (C) 2017 Savoir-faire Linux

# This file if part of OdooLightWorkflow.
#
# OdooLightWorkflow free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OdooLightWorkflow is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'Light Workflow',
    'version': '10.0.1.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Others',
    'summary': 'A lightweight Odoo workflow engine.',
    'depends': [],
    'external_dependencies': {
        'python': [
            'transitions',
        ],
    },
    'data': [
    ],
    'installable': True,
    'application': False,
}
