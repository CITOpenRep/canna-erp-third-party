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
    var basic_fields = require("web.basic_fields");

    ReconciliationModel.StatementModel.include({
        init: function() {
            this._super.apply(this, arguments);
            this.quickCreateFieldsStandard = [
                "account_id",
                "amount",
                "analytic_account_id",
                "label",
                "tax_ids",
                "force_tax_included",
                "analytic_tag_ids",
                "to_check",
            ];
        },

        reload: function() {
            var self = this;
            var def_reload = this._super();

            var def_dims = self
                ._rpc({
                    model: self.context.active_model,
                    method: "search_read",
                    fields: ["company_id"],
                    domain: [["id", "=", self.context.active_id]],
                })
                .then(function(company) {
                    self.company_id = company[0].company_id[0];
                    self._rpc({
                        model: "account.account",
                        method: "search_read",
                        fields: ["id", "analytic_dimensions"],
                        domain: [
                            ["analytic_dimension_policy", "in", ["always", "posted"]],
                            ["deprecated", "=", false],
                            ["company_id", "=", self.company_id],
                        ],
                    }).then(function(accounts) {
                        self.AnalyticDimensionPolicyRequiredAccounts = accounts;
                        self.AnalyticDimensions = [];
                        self.NewAnalyticDimensions = [];
                        self.NewAnalyticDimensionsFields = [];
                        self._rpc({
                            model: "account.move.line",
                            method: "get_analytic_dimension_fields",
                            args: [self.company_id],
                        }).then(function(dimensions) {
                            self.AnalyticDimensions = _.pluck(dimensions, "name");
                            _.each(dimensions, function(field) {
                                if (!self.quickCreateFields.includes(field.name)) {
                                    self.quickCreateFields.push(field.name);
                                }
                                if (
                                    !self.quickCreateFieldsStandard.includes(field.name)
                                ) {
                                    self.NewAnalyticDimensions.push(field.name);
                                    self.NewAnalyticDimensionsFields.push(field);
                                }
                            });
                        });
                    });
                });
            return Promise.all([def_reload, def_dims]).then(function() {
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
                _.each(self.model.NewAnalyticDimensionsFields, function(field) {
                    if (field.type === "many2one") {
                        self.fields[
                            field.name
                        ] = new relational_fields.FieldMany2One(
                            self,
                            field.name,
                            record,
                            {mode: "edit", attrs: {can_create: false}}
                        );
                    } else if (field.type === "many2many") {
                        self.fields[
                            field.name
                        ] = new relational_fields.FieldMany2ManyTags(
                            self,
                            field.name,
                            record,
                            {mode: "edit", attrs: {can_create: false}}
                        );
                    } else if (field.type === "selection") {
                        self.fields[
                            field.name
                        ] = new relational_fields.FieldSelection(
                            self,
                            field.name,
                            record,
                            {mode: "edit"}
                        );
                    } else {
                        self.fields[field.name] = new basic_fields.FieldChar(
                            self,
                            field.name,
                            record,
                            {mode: "edit"}
                        );
                    }
                    self.fields[field.name].appendTo(
                        self.$el.find(".create_" + field.name + " .o_td_field")
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
                var policy = this.model.AnalyticDimensionPolicyRequiredAccounts.find(
                    item => item.id === account_id
                );
                _.each(this.model.AnalyticDimensions, function(dim) {
                    if (self.fields[dim]) {
                        if (policy) {
                            var analytic_dimensions = policy.analytic_dimensions.split(
                                ","
                            );
                            if (analytic_dimensions.includes(dim)) {
                                self.fields[dim].$el.addClass("o_required_modifier");
                            } else {
                                self.fields[dim].$el.removeClass("o_required_modifier");
                            }
                        } else {
                            self.fields[dim].$el.removeClass("o_required_modifier");
                        }
                    }
                });
            }
        },
    });
});
