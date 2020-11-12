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
    var relational_fields = require("web.relational_fields");

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
                self.AnalyticDimensionPolicyRequired_account_ids = _.pluck(
                    accounts,
                    "id"
                );
            });

            this.AnalyticDimensions = [];
            this.NewAnalyticDimensions = [];
            this.NewAnalyticDimensionsFields = [];
            var def_dims = self
                ._rpc({
                    model: "account.move.line",
                    method: "get_analytic_dimension_fields",
                })
                .then(function(result) {
                    self.AnalyticDimensions = _.pluck(result, "name");
                    _.each(result, function(field) {
                        if (!self.quickCreateFields.includes(field.name)) {
                            self.quickCreateFields.push(field.name);
                            self.NewAnalyticDimensions.push(field.name);
                            self.NewAnalyticDimensionsFields.push(field);
                        }
                    });
                });

            return Promise.all([def_reload, def_accounts, def_dims]).then(function() {
                return def_reload;
            });
        },

        _formatQuickCreate: function(line, values) {
            var prop = this._super(line, values);
            _.each(this.NewAnalyticDimensions, function(field) {
                prop[field] = false;
            });
            return prop;
        },

        makeRecord: function(model, fields, fieldInfo) {
            if (
                model === "account.bank.statement.line" &&
                fields.some(field => field.name === "amount")
            ) {
                _.each(this.NewAnalyticDimensionsFields, function(field) {
                    fields.push(field);
                });
                _.extend(
                    fieldInfo,
                    _.pluck(this.NewAnalyticDimensionsFields, "string")
                );
            }
            return this._super(model, fields, fieldInfo);
        },

        _formatToProcessReconciliation: function(line, prop) {
            var result = this._super(line, prop);
            _.each(this.NewAnalyticDimensions, function(field) {
                if (prop[field]) {
                    result[field] = prop[field].id ? prop[field].id : prop[field];
                }
            });
            return result;
        },
    });

    ReconciliationRenderer.LineRenderer.include({
        _renderCreate: function(state) {
            var self = this;
            return Promise.resolve(this._super(state)).then(function() {
                var record = self.model.get(self.handleCreateRecord);
                _.each(self.model.NewAnalyticDimensions, function(field) {
                    self.fields[field] = new relational_fields.FieldMany2One(
                        self,
                        field,
                        record,
                        {mode: "edit"}
                    );
                    self.fields[field].appendTo(
                        self.$el.find(".create_" + field + " .o_td_field")
                    );
                });
            });
        },

        _onFieldChanged: function(event) {
            var self = this;
            this._super(event);
            var fieldName = event.target.name;

            if (fieldName === "account_id") {
                var account_id = event.data.changes.account_id.id;
                if (
                    this.model.AnalyticDimensionPolicyRequired_account_ids.includes(
                        account_id
                    )
                ) {
                    _.each(this.model.AnalyticDimensions, function(dim) {
                        if (self.fields[dim]) {
                            self.fields[dim].$el.addClass("o_required_modifier");
                        }
                    });
                } else {
                    _.each(this.model.AnalyticDimensions, function(dim) {
                        if (self.fields[dim]) {
                            self.fields[dim].$el.removeClass("o_required_modifier");
                        }
                    });
                }
            }
        },
    });
});
