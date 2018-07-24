# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class scheduler_demo(models.Model):
    _name = 'scheduler.demo'
    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates')
    lastModified = fields.Datetime('Last updated')
