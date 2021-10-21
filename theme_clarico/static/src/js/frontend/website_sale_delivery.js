odoo.define('theme_clarico.replace_strategy', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    /* Handle interactive replace choice + cart update */

    var _onStrategyClick = function (ev) {
        var strategy_id = $(ev.currentTarget).val();
        var values = {'strategy_id': strategy_id};
        dp.add(ajax.jsonRpc('/shop/update_strategy', 'call', values));
    };

    var $strategies = $("#preferred_method input[name='strategy_type']");
    $strategies.click(_onStrategyClick);

    var _onStrategyObs = function (ev) {
        var strategy_obs_text = $(ev.currentTarget).val();
        var values = {'strategy_obs': strategy_obs_text}
        dp.add(ajax.jsonRpc('/shop/update_strategy', 'call', values));
    }

    var $strategy_obs_text = $("#preferred_method_obs input[name='replace_obs_text']");
    $strategy_obs_text.change(_onStrategyObs);

});
