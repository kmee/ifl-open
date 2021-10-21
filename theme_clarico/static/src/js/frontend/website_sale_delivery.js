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

    // contribution
    var _onContributionClick = function (ev) {
        var contribution_input = $(ev.currentTarget).val();
        if (contribution_input == -1) {
            contribution_input = $("#custom_contribution input[name='contribution_int']").val();
        }
        var values = {'contribution': contribution_input}
        dp.add(ajax.jsonRpc('/shop/update_strategy', 'call', values));
    }

    var $contribution_input = $("#custom_contribution input[name='contribution_input']");
    $contribution_input.click(_onContributionClick);

    var _onContributionChange = function (ev) {
        var $contribution_value = $("#custom_contribution input[name='contribution_int']")
        if ($contribution_value.val() < 0) {
            $contribution_value[0].value = 0;
        }
        $("#custom_contribution input[name='contribution_input']")[1].click();
    }

    var $contribution_int = $("#custom_contribution input[name='contribution_int']");
    $contribution_int.change(_onContributionChange);

});
