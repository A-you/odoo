# coding=utf-8

from ..routes import robot
from .. import client
from openerp.http import request
import time


@robot.subscribe
def subscribe(message):
    serviceid = message.target
    openid = message.source

    info = client.wxclient.get_user_info(openid)
    info['group_id'] = str(info['groupid'])
    # rn:转变时间戳格式
    info['subscribe_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info['subscribe_time']))
    env = request.env()
    rs = env['wx.user'].sudo().search([('openid', '=', openid)])
    if not rs.exists():
        env['wx.user'].sudo().create(info)
    else:
        rs.write({'subscribe': True, 'subscribe_time': info['subscribe_time']})

    return "您终于来了！欢迎关注"


@robot.unsubscribe
def unsubscribe(message):
    serviceid = message.target
    openid = message.source
    env = request.env()
    rs = env['wx.user'].sudo().search([('openid', '=', openid)])
    if rs.exists():
        # rn:计划修改为发往用户订阅状态，而不是删除
        rs.write({'subscribe': False})
        # rs.unlink()

    return "欢迎下次光临！"


@robot.view
def url_view(message):
    print 'obot.view---------', message
