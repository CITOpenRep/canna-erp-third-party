/*
# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

odoo.define("account_analytic_dimensions_policy.analytic_dimensions_policy", function(
    require
) {
    "use strict";

    var ReconciliationModel = require("account.ReconciliationModel");
    var ReconciliationRenderer = require("account.ReconciliationRenderer");

    ReconciliationModel.StatementModel.include({
        reload: function() {
            var self = this;
            var def_reload = this._super();

            var def_accounts = this._rpc({
                model: "account.account",
                method: "search_read",
                fields: ["id"],
                domain: [
                    ["analytic_dimension_policy", "in", ["always", "posted"]],
                    ["deprecated", "=", false],
                ],
            }).then(function(accounts) {
                self.analytic_dimension_policy_required_account_ids = _.pluck(
                    accounts,
                    "id"
                );
            });

            var def_dims = self
                ._rpc({
                    model: "account.move.line",
                    method: "get_analytic_dimensions",
                })
                .then(function(dims) {
                    self.analytic_dimensions = dims;
                });

            return Promise.all([def_reload, def_accounts, def_dims]).then(function() {
                return def_reload;
            });
        },
    });

    ReconciliationRenderer.LineRenderer.include({
        _onFieldChanged: function(event) {
            var self = this;
            this._super(event);
            var fieldName = event.target.name;

            if (fieldName === "account_id") {
                var account_id = event.data.changes.account_id.id;
                if (
                    this.model.analytic_dimension_policy_required_account_ids.includes(
                        account_id
                    )
                ) {
                    _.each(this.model.analytic_dimensions, function(dim) {
                        if (self.fields[dim]) {
                            self.fields[dim].$el.addClass("o_required_modifier");
                        }
                    });
                } else {
                    _.each(this.model.analytic_dimensions, function(dim) {
                        if (self.fields[dim]) {
                            self.fields[dim].$el.removeClass("o_required_modifier");
                        }
                    });
                }
            }
        },
    });
});
