# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, tools, _


class LoanAttachment(models.Model):
    # _name = 'loan.attachment'
    # _description = u'审贷附件'
    _inherit = 'ir.attachment'

    # _rec_name = 'credit_id'
    # _order = 'state,order desc'

    @api.model
    def _file_write(self, value, checksum):
        # print len(value)
        # bin_value = value.decode('base64')
        if self.mimetype == u'image/jpeg':
            value = tools.image_resize_image_big(value)
        # com_value = ''
        # print len(value)
        return super(LoanAttachment, self)._file_write(value, checksum)
        # fname, full_path = self._get_path(bin_value, checksum)
        # if not os.path.exists(full_path):
        #     try:
        #         with open(full_path, 'wb') as fp:
        #             fp.write(bin_value)
        #         # add fname to checklist, in case the transaction aborts
        #         self._mark_for_gc(fname)
        #     except IOError:
        #         _logger.info("_file_write writing %s", full_path, exc_info=True)
        # return fname
