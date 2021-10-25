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
            if ($("#custom_contribution input[name='contribution_int']").val() == false) {
                contribution_input = 0;
            } else {
                contribution_input = $("#custom_contribution input[name='contribution_int']").val();
            }
        }
        var values = {'contribution': contribution_input}
        dp.add(ajax.jsonRpc('/shop/update_strategy', 'call', values));
        // UPDATE FRONT END VALUES
        var $contribution_percent = $("span[name='contribution_percent']");
        $contribution_percent[0].innerText = contribution_input;

        var _formatToMonetary = function (value) {
            return(value.toFixed(2).toString().replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, "."));
        }

        // calc contribution
        var $subtotal_no_contribution = $('#order_total_untaxed_hidden .sub_total_hidden');
        var subtotal_no_contribution = parseFloat($subtotal_no_contribution[0].innerText);
        var $contribution_price = $("span[name='contribution_price']");
        $contribution_price[0].innerText = subtotal_no_contribution * contribution_input / 100;

        //calc subtotal com contribuicao
        var $subtotal_with_contribution = $('#order_total_untaxed .oe_currency_value');
        var subtotal_with_contribution = (subtotal_no_contribution * (1 + (contribution_input/100)));
        $subtotal_with_contribution[0].innerText = _formatToMonetary(subtotal_with_contribution);

        //calc product price for each prod
        var $product_with_contribution = $('#cart_products .subtotal_show');
        var $product_no_contribution = $('#cart_products .subtotal_hidden');
        var product_with_contribution;
        var product_no_contribution;
        for (var pos = 0; pos < $product_with_contribution.length; pos++) {
            product_no_contribution = parseFloat($product_no_contribution[pos].innerText);
            product_with_contribution = (product_no_contribution * (1 + (contribution_input/100)));
            $product_with_contribution[pos].innerText = _formatToMonetary(product_with_contribution);
        }

        //calc total
        var $delivery = $('#order_delivery .oe_currency_value');
        var $total = $('#order_total .oe_currency_value');
        var delivery = parseFloat($delivery[0].innerText);
        $total[0].innerText = _formatToMonetary(subtotal_with_contribution + delivery);

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
