<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-container fluid fill-height
                 class="pa-0">

        <div ref="map"
             class="map" />

        <v-card outlined
                class="map-stats-container">
            <v-card-text>
                <v-row dense>
                    <v-col cols="12">
                        STATS
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>

        <v-row dense class="map-options-container">
            <v-col cols="12">
                <v-btn fab
                       elevation="0"
                       style="border: 2px solid !important;"
                       :color="showAfterLayer ? 'accent' : 'disabled'"
                       :class="{ 'map-option-inactive': !showAfterLayer }"
                       @click="onToggleLayers">
                    <v-icon large>
                        mdi-flash-alert
                    </v-icon>
                </v-btn>
            </v-col>
            <v-col cols="12">
                <v-btn fab
                       elevation="0"
                       style="border: 2px solid !important;"
                       :color="showHeatmap ? 'accent' : 'disabled'"
                       :class="{ 'map-option-inactive': !showHeatmap }"
                       @click="onToggleHeatmap">
                    <v-icon large>
                        mdi-dots-hexagon
                    </v-icon>
                </v-btn>
            </v-col>
            <v-col cols="12">
                <v-btn fab
                       elevation="0"
                       style="border: 2px solid !important;"
                       :color="showDamagePolygons ? 'accent' : 'disabled'"
                       :class="{ 'map-option-inactive': !showDamagePolygons }"
                       @click="onToggleDamagePolygons">
                    <v-icon large>
                        mdi-vector-polygon
                    </v-icon>
                </v-btn>
            </v-col>
        </v-row>
    </v-container>
</template>

<!--suppress JSMethodCanBeStatic, JSUnusedGlobalSymbols -->
<script lang="ts">

import * as L from "leaflet";
import "leaflet.heat";

import {
    Component,
    Ref,
    Vue,
    Watch,
} from "vue-property-decorator";

import { getModule } from "vuex-module-decorators";
import { AppModule } from "@/store/app";

import {
    NavigationGuardNext,
    Route,
} from "vue-router";

import * as outgoing from "@/router/outgoing";

import {
    IDisasterZone,
    ILatLng,
} from "@/models";

interface IViewOptions {
    center: ILatLng;
    zoom: number;
    fly?: boolean;
}

function extractMapViewOptions(text: string): IViewOptions | null {
    const matches = /@(-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(\d+(\.\d+)?)z/.exec(text);
    if(!matches) {
        return null;
    }

    return {
        center: {
            lat: parseFloat(matches[1]),
            lng: parseFloat(matches[3]),
        },
        zoom: parseFloat(matches[5]),
    };
}

async function fetchGeoJSON(endpointUrl: string, bounds: [ILatLng, ILatLng], limit: number) {
    const url = new URL(endpointUrl);

    url.searchParams.append("ne_lat", bounds[0].lat.toString());
    url.searchParams.append("ne_lng", bounds[0].lng.toString());
    url.searchParams.append("sw_lat", bounds[1].lat.toString());
    url.searchParams.append("sw_lng", bounds[1].lng.toString());
    url.searchParams.append("limit", limit.toString());

    const response = await fetch(url.toString());
    return await response.json();
}

async function fetchHeatmap(endpointUrl: string) {
    const response = await fetch(endpointUrl);
    return await response.json();
}

@Component
export default class HomeView extends Vue {
    private readonly app = getModule(AppModule);

    @Ref("map") private mapRef!: HTMLElement;
    private map!: L.Map;

    private showAfterLayer = true;
    private showHeatmap = false;
    private showDamagePolygons = false;

    private detailZoomLevel = 15;
    private amenityCache: L.GeoJSON | null = null;
    private affectedStructureCache: L.GeoJSON | null = null;
    private unaffectedStructureCache: L.GeoJSON | null = null;

    private beforeLayers = [
        L.tileLayer("http://159.223.58.255:5000/rgb/before/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]", {
            attribution: "&copy; <a href=\"https://www.maxar.com/open-data\">Maxar</a>",
        }),
    ];

    private afterLayers = [
        L.tileLayer("http://159.223.58.255:5000/rgb/after/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]", {
            attribution: "&copy; <a href=\"https://www.maxar.com/open-data\">Maxar</a>",
        }),
    ];

    private updateRoute(view: IViewOptions) {
        const latitude = view.center.lat.toFixed(7);
        const longitude = view.center.lng.toFixed(7);
        const zoom = view.zoom.toFixed(0);

        const options = `@${latitude},${longitude},${zoom}z`;
        if(this.$route.params.options !== options) {
            this.$router.replace({
                name: this.$route.name!,
                params: {
                    options,
                },
            }).catch();
        }
    }

    private navigateToRouteView() {
        if(this.$route.params.options) {
            const view = extractMapViewOptions(this.$route.params.options);
            if(view) {
                this.setView(view);
            }
        }
    }

    private visibleLayers(layers: "before" | "after") {
        this.beforeLayers.forEach(l => l.remove());
        this.afterLayers.forEach(l => l.remove());

        if(layers === "before") {
            this.beforeLayers.forEach(l => l.addTo(this.map));
        } else {
            this.afterLayers.forEach(l => l.addTo(this.map));
        }
    }

    // TODO: Change URL depending on selected disaster.
    private async updateAmenities() {
        if(this.getView().zoom <= this.detailZoomLevel) {
            this.amenityCache?.remove();
            return;
        }

        const bounds = this.getBounds();
        const features = await fetchGeoJSON("http://127.0.0.1:8088/geo/vegas/amenities", bounds, 300);

        const layer = L.geoJSON(features, {
            pointToLayer(geoJsonPoint, latlng) {
                return L.marker(latlng, {
                    icon: L.icon({
                        iconUrl: outgoing.publicUrl("favicon.ico"),
                        iconSize: [24, 24],
                    }),
                });
            },
        }).addTo(this.map);

        this.amenityCache?.remove();
        this.amenityCache = layer;
    }

    // TODO: Change URL depending on selected disaster.
    private async updateAffectedStructures() {
        if(this.getView().zoom <= this.detailZoomLevel) {
            this.affectedStructureCache?.remove();
            return;
        }

        const bounds = this.getBounds();
        const features = await fetchGeoJSON("http://127.0.0.1:8088/geo/vegas/structures-affected", bounds, 3000);

        const layer = L.geoJSON(features, {
            style: {
                color: this.$vuetify.theme.currentTheme.error?.toString(),
            },
        }).addTo(this.map);

        this.affectedStructureCache?.remove();
        this.affectedStructureCache = layer;
    }

    // TODO: Change URL depending on selected disaster.
    private async updateUnaffectedStructures() {
        if(this.getView().zoom <= this.detailZoomLevel) {
            this.unaffectedStructureCache?.remove();
            return;
        }

        const bounds = this.getBounds();
        const features = await fetchGeoJSON("http://127.0.0.1:8088/geo/vegas/structures-unaffected", bounds, 3000);

        const layer = L.geoJSON(features, {
            style: {
                color: this.$vuetify.theme.currentTheme.success?.toString(),
            },
        }).addTo(this.map);

        this.unaffectedStructureCache?.remove();
        this.unaffectedStructureCache = layer;
    }

    private onViewChanged() {
        this.updateRoute(this.getView());

        this.updateAmenities();
        this.updateAffectedStructures();
        this.updateUnaffectedStructures();
    }

    private onToggleLayers() {
        this.showAfterLayer = !this.showAfterLayer;
        this.visibleLayers(this.showAfterLayer ? "after" : "before");
    }

    private onToggleHeatmap() {
        this.showHeatmap = !this.showHeatmap;
    }

    private onToggleDamagePolygons() {
        this.showDamagePolygons = !this.showDamagePolygons;
    }

    private getView(): IViewOptions {
        return {
            center: this.map.getCenter(),
            zoom: this.map.getZoom(),
        };
    }

    private setView(options: Partial<IViewOptions>) {
        const center = options.center || this.getView().center;
        const zoom = options.zoom || this.getView().zoom;

        if(options.fly) {
            this.map.flyTo(center, zoom);
        } else {
            this.map.setView(center, zoom);
        }
    }

    private getBounds(): [ILatLng, ILatLng] {
        const bounds = this.map.getBounds();
        return [
            bounds.getNorthEast(),
            bounds.getSouthWest(),
        ];
    }

    @Watch("app.selectedDisasterZone")
    onDisasterZoneSelected(disasterZone: IDisasterZone | null): void {
        if(disasterZone) {
            this.setView({
                center: disasterZone.center,
                zoom: 10,
                fly: true,
            });
        }
    }

    beforeRouteUpdate(to: Route, from: Route, next: NavigationGuardNext): void {
        next(vm => (vm as HomeView).navigateToRouteView());
    }

    mounted(): void {
        this.map = L.map(this.mapRef, {
            minZoom: 2,
            maxZoom: 18,
            maxBounds: [
                [-90, -180],
                [90, 180],
            ],
        }).setView([20, 0], 3);

        L.control.scale().addTo(this.map);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors",
        }).addTo(this.map);

        this.visibleLayers("before");

        this.map.on("moveend", () => this.onViewChanged());
        this.map.on("zoomend", () => this.onViewChanged());

        this.navigateToRouteView();

        // TODO: Load/hide per disaster.
        ((async () => {
            const heatmap = await fetchHeatmap("http://127.0.0.1:8088/geo/vegas/structures-affected/heatmap");
            (L as any).heatLayer(
                heatmap, {
                    radius: 20,
                    minOpacity: 0.7,
                },
            ).addTo(this.map);
        })());
    }

    beforeDestroy(): void {
        this.map.remove();
    }
}

</script>

<style lang="scss" scoped>

$side-offset: 20px;

.map {
    display: block;
    z-index: 0;
    width: 100%;
    height: 100%;
}

.map-stats-container {
    position: absolute;
    left: $side-offset;
    bottom: $side-offset;

    background-color: rgba(white, 0.8) !important;
}

.map-options-container {
    position: absolute;
    right: $side-offset;
    bottom: $side-offset;

    text-align: end;
}

.map-option-inactive {
    opacity: 0.6;
}

</style>
