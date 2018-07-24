# coding:utf-8

from odoo import models, fields
import xlrd
import base64


class HmRegion(models.Model):
    _name = "hm.region"

    xls = fields.Binary('XLS File')

    def btn_import(self, context=None):
        print(self.ids)
        for wiz in self.browse(self.ids):
            # print(wiz.xls)
            if not wiz.xls:
                continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
            sheets = excel.sheets()
            # print(sheets)
            for sh in sheets:
                for row in range(1, sh.nrows):
                    state = sh.cell(row, 0).value
                    city = sh.cell(row, 1).value
                    district = sh.cell(row, 2).value
                    jp = sh.cell(row, 3).value

                    # read state
                    states = self.env['res.country.state'].search([('name', '=', state)])
                    if len(states):
                        cities = self.env['hm.city'].search([('name', '=', city)])
                        if len(cities):
                            dises = self.env['hm.district'].search([('name', '=', district)])
                            if len(dises):
                                continue
                            else:
                                self.env['hm.district'].create({'name': district, 'city': cities[0].id})
                        else:
                            c_id = self.env['hm.city'].create({'name': city, 'state': states[0].id})

                            self.env['hm.district'].create({'name': district, 'city': c_id.id})
                    else:
                        china = self.env['res.country'].search([('name', '=', 'China')])
                        if len(china):

                            s_id = self.env['res.country.state'].create(
                                {'name': state, 'country_id': china[0].id, 'code': jp})
                            c_id = self.env['hm.city'].create({'name': city, 'state': s_id.id})
                            self.env['hm.district'].create({'name': district, 'city': c_id.id})
                        else:
                            ch_id = self.env['res.country'].create({'name': 'China'})

                            s_id = self.env['res.country.state'].create(
                                {'name': state, 'country_id': ch_id.id, 'code': jp})
                            c_id = self.env['hm.city'].create({'name': city, 'state': s_id.id})
                            self.env['hm.district'].create({'name': district, 'city': c_id.id})

