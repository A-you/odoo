# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class LoanRecordAutovacuum(models.TransientModel):
    _name = 'loan.autovacuum'
    _description = "Loan - Delete old records"

    @api.model
    def autovacuum(self, days):
        """Delete all records older than ``days`` not in ['approved',]. This includes:

        Called from a cron.
        """
        days = (days > 0) and int(days) or 0
        deadline = datetime.now() - timedelta(days=days)
        data_models = (
            'loan.apply',
            'loan.loan',
            'loan.credit',
        )
        for data_model in data_models:
            records = self.env[data_model].search(
                [('create_date', '<=', fields.Datetime.to_string(deadline)),
                 ('state', 'not in', ['approved', 'refused'])])
            nb_records = len(records)
            # records.unlink()
            records.write({'active': False})
            _logger.info(
                u"AUTOVACUUM - %s '%s' records deactived",
                nb_records, data_model)
        return True

    @api.model
    def autovacuum_credit(self, days):
        """Delete all credit older than ``days`` in ['approved',]. This includes:

        Called from a cron.
        """
        days = (days > 0) and int(days) or 0
        deadline = datetime.now() - timedelta(days=days)
        data_models = (
            'loan.credit',
        )
        for data_model in data_models:
            records = self.env[data_model].search(
                [('create_date', '<=', fields.Datetime.to_string(deadline)),
                 ('state', 'in', ['approved', ]),
                 ('tag_ids.name', 'not in', ['本人', ])])
            nb_records = len(records)
            # records.unlink()
            records.write({'active': False})
            _logger.info(
                u"AUTOVACUUM - %s '%s' credits deactived",
                nb_records, data_model)
        return True
