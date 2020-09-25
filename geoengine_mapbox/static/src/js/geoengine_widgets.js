odoo.define('geoengine_mapbox.mapbox_geoengine_widgets', function (require) {
    "use strict";

    var geoengine_widgets = require('base_geoengine.geoengine_widgets');

    var FieldGeoEngineEditMap = geoengine_widgets.FieldGeoEngineEditMap.include({ // eslint-disable-line max-len

        _renderMap: function () {
            if (!this.map) {
                var $el = this.$el[0];
                $($el).css({
                    width: '100%',
                    height: '100%',
                });
                try {
                    console.log("Trying to load the map using MapBox API");
                    var partner_longitude = this.record.data.partner_longitude;
                    var partner_latitude = this.record.data.partner_latitude;
                    var coordinates = [partner_latitude, partner_longitude];
                    this._rpc({
                        model: 'res.partner',
                        method: 'get_mapbox_client_id',
                    }).then(function (result) {
                        if (this.map) {
                            this.map.remove();
                        }
                        mapboxgl.accessToken = result;
                        this.map = new mapboxgl.Map({
                            container: 'geo_point',
                            style: 'mapbox://styles/mapbox/streets-v11',
                            center: coordinates,
                            zoom: 15,
                        });
                        new mapboxgl.Marker()
                            .setLngLat(coordinates)
                            .addTo(this.map);
                        $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
                    }.bind(this));
                } catch (error) {
                    console.log("MapBox API failed, loading the map using OpenStreet API. Error:", error);
                    this._rpc({
                        model: 'res.partner',
                        method: 'send_mapbox_fail_mail',
                        args: [error],
                    }).then(function (result) {

                        this.map = new ol.Map({
                            layers: this.rasterLayers,
                            target: $el,
                            view: new ol.View({
                                center: [0, 0],
                                zoom: 15,
                            }),
                        });
                        this.map.addLayer(this.vectorLayer);
                        this.format = new ol.format.GeoJSON({
                            internalProjection: this.map.getView().getProjection(),
                            externalProjection: 'EPSG:' + this.srid,
                        });
                        $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
                        this._setValue(this.value);
                        if (this.mode !== 'readonly' &&
                            !this.get('effective_readonly')) {
                            this._setupControls();
                            this.drawControl.setActive(true);
                            this.modifyControl.setActive(true);
                            this.clearmapControl.element.children[0].disabled = false;
                        }
                    });
                }

            }
        },

    });

    return FieldGeoEngineEditMap;

});
