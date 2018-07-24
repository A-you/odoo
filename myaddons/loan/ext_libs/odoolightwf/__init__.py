# -*- coding: utf-8 -*-
# OdooLightWorkflow, a lightweight workflow engine for Odoo
# Copyright (C) 2016,2017 Savoir-faire Linux

# This file if part of OdooLightWorkflow.
#
# OdooLightWorkflow is free software: you can redistribute it and/or modify it
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
from functools import partial

from odoo import api, models
from odoo.exceptions import ValidationError
from transitions import Machine, MachineError

CALLBACK_CATEGORIES = ('conditions', 'unless', 'before', 'after', 'prepare')


def normalize_transition(t):
    if isinstance(t, list):
        newtrans = {
            'trigger': t[0],
            'source': t[1],
            'dest': t[2],
            'conditions': (len(t) > 3 and t[3]) or [],
            'unless': (len(t) > 4 and t[4]) or [],
            'before': (len(t) > 5 and t[5]) or [],
            'after': (len(t) > 6 and t[6]) or [],
            'prepare': (len(t) > 7 and t[7]) or [],
        }
    elif isinstance(t, dict):
        newtrans = {
            'trigger': t['trigger'],
            'source': t['source'],
            'dest': t['dest'],
            'conditions': t.get('conditions', None) or [],
            'unless': t.get('unless', None) or [],
            'before': t.get('before', None) or [],
            'after': t.get('after', None) or [],
            'prepare': t.get('prepare', None) or [],
        }
    else:
        raise TypeError('Not a valid transition: %s' % t)
    for cat in CALLBACK_CATEGORIES:
        item = newtrans[cat]
        if not isinstance(item, list):
            newtrans[cat] = [item]
    return newtrans


class WorkflowModel(models.BaseModel):
    _auto = True
    _register = False
    _transient = False

    _machine = None

    @api.multi
    def _create_machine(self):
        self.ensure_one()
        callbacks = []
        ts = []
        for t in self._transitions:
            norm_t = normalize_transition(t)
            for cat in CALLBACK_CATEGORIES:
                callbacks += norm_t[cat]
            norm_t['after'].append('_update_model_state')
            ts.append(norm_t)

        self._transitions = ts

        states = [t[0] for t in self._states]
        machine = Machine(
            states=states, transitions=ts, initial=self.state)

        # TODO: _update_model_state shouldn't be in callbacks to begin with
        callbacks = set(callbacks) - set(('_update_model_state',))
        for cb in callbacks:
            setattr(machine, cb, partial(getattr(self, cb)))

        def _update_model_state():
            self.state = machine.state

        machine._update_model_state = _update_model_state
        return machine

    @property
    def machine(self):
        if not self._machine:
            self._machine = self._create_machine()
        return self._machine


def trigger(fname, fdoc=None):
    @api.multi
    def func(self):
        self.ensure_one()
        try:
            res = getattr(self.machine, fname)()
        except MachineError:
            state = dict(self._states)[self.state]
            action = fdoc if fdoc else fname
            # msg = 'Action "%s" cannot be done from state "%s"'
            msg = u'在当前 "%s" 状态下，不能执行 "%s"'
            # msg = msg % (action, state)
            msg = msg % (state, action)
            raise WorkflowError(msg)
        if not res:
            action = fdoc if fdoc else fname
            # msg_parts = ['These conditions must be met to %s:' % action]
            msg_parts = [u'必需满足以下条件 %s:' % action]
            t = [t for t in self._transitions
                 if t['trigger'] == fname and t['source'] == self.state][0]
            conds = t.get('conditions', [])
            for cd in conds:
                cdfunc = getattr(self, cd)
                msg = getattr(cdfunc, '__doc__', cdfunc.__name__)
                if msg:
                    msg_parts.append(msg)
            raise WorkflowError('\n'.join(msg_parts))
        return res

    func.__name__ = fname
    func.__doc__ = fdoc
    return func


class WorkflowError(ValidationError):
    def __init__(self, msg):
        super(WorkflowError, self).__init__(msg)
