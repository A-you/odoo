odoo.define('tfs_api_info', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var framework = require('web.framework');

    var Dashboard = Widget.extend({
        template: 'tfs_api_info',
    });

    core.action_registry.add('tfs_api_info.main', Dashboard);

    return {
        Dashboard: Dashboard,
    };

});
