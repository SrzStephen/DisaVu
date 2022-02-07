<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-container fluid fill-height
                 class="pa-0">

        <div ref="map"
             class="map" />

        <!--
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
        -->

        <v-row dense class="map-options-container">
            <v-col cols="12">
                <v-badge left bordered overlap
                         :color="visibleLayer === 'none' ? 'disabled' : visibleLayer === 'before' ? 'success' : 'error'"
                         :content="visibleLayer">
                    <v-btn fab
                           elevation="0"
                           style="border: 2px solid !important;"
                           :color="visibleLayer === 'none' ? 'disabled' : visibleLayer === 'before' ? 'success' : 'error'"
                           :class="{ 'map-option-inactive': visibleLayer === 'none' }"
                           @click="onToggleLayers">
                        <v-icon large>
                            {{ visibleLayer === "after" ? "mdi-flash-alert" : "mdi-flash" }}
                        </v-icon>
                    </v-btn>
                </v-badge>
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
                       :color="showAmenities ? 'accent' : 'disabled'"
                       :class="{ 'map-option-inactive': !showAmenities }"
                       @click="onToggleAmenities">
                    <v-icon large>
                        mdi-hospital-building
                    </v-icon>
                </v-btn>
            </v-col>
            <v-col cols="12">
                <v-btn fab
                       elevation="0"
                       style="border: 2px solid !important;"
                       :color="showStructures ? 'accent' : 'disabled'"
                       :class="{ 'map-option-inactive': !showStructures }"
                       @click="onToggleDamagePolygons">
                    <v-icon large>
                        mdi-vector-polygon
                    </v-icon>
                </v-btn>
            </v-col>
        </v-row>

        <v-overlay :value="pending">
            <v-progress-circular indeterminate
                                 size="80" />
        </v-overlay>
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

type VisibleLayer = "none" | "before" | "after";

function capitalizeString(text: string) {
    return text.charAt(0).toUpperCase() + text.slice(1);
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

async function fetchDisasterZones() {
    const response = await fetch("disaster-zones.json");
    return await response.json();
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

const AMENITY_LIMIT = 4000;
const AMENITY_ZOOM_LEVEL = 14;

const STRUCTURE_LIMIT = 6000;
const STRUCTURE_ZOOM_LEVEL = 17;

const SUPPORTED_AMENITIES = [
    "bank",
    "bus_station",
    "childcare",
    "cinema",
    "clinic",
    "college",
    "community_centre",
    "courthouse",
    "dentist",
    "doctors",
    "ferry_terminal",
    "fire_station",
    "fuel",
    "hospital",
    "kindergarten",
    "library",
    "nursing_home",
    "pharmacy",
    "place_of_worship",
    "police",
    "post_office",
    "prep_school",
    "prison",
    "public_building",
    "school",
    "shelter",
    "townhall",
    "university",
];

@Component
export default class HomeView extends Vue {
    private readonly app = getModule(AppModule);
    private pending = true;

    @Ref("map") private mapRef!: HTMLElement;
    private map!: L.Map;

    private visibleLayer: VisibleLayer = "none";

    private showHeatmap = true;
    private showAmenities = true;
    private showStructures = false;

    private amenityCache: L.GeoJSON | null = null;
    private affectedStructureCache: L.GeoJSON | null = null;
    private unaffectedStructureCache: L.GeoJSON | null = null;

    private beforeLayer: L.TileLayer | null = null;
    private afterLayer: L.TileLayer | null = null;
    private heatmapLayer: L.TileLayer | null = null;

    private updateRoute() {
        const view = this.getView();
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

    private async updateAmenities() {
        if(this.getView().zoom < AMENITY_ZOOM_LEVEL) {
            this.amenityCache?.remove();
            return;
        }

        if(!this.showAmenities) {
            this.amenityCache?.remove();
            return;
        }

        const amenitiesUrl = this.app.selectedDisasterZone?.amenitiesUrl;
        if(!amenitiesUrl) {
            return;
        }

        const bounds = this.getBounds();
        const features = (await fetchGeoJSON(amenitiesUrl, bounds, AMENITY_LIMIT))
            .filter((f: any) => SUPPORTED_AMENITIES.includes(f?.properties?.amenity));

        const layer = L.geoJSON(features, {
            pointToLayer(point, coordinates) {
                const amenity = {
                    name: point.properties.name,
                    type: point.properties.amenity.split("_").map(capitalizeString).join(" "),
                    icon: `${point.properties.amenity}.svg`,
                };

                const tooltip = `${amenity.name} (${amenity.type} @ ${coordinates.lat.toFixed(7)}, ${coordinates.lng.toFixed(7)})`;

                const marker = L.marker(coordinates, {
                    alt: tooltip,
                    icon: L.icon({
                        iconUrl: outgoing.publicUrl("map/markers/amenities", amenity.icon),
                        iconSize: [32, 32],
                    }),
                });

                marker.bindTooltip(tooltip, {
                    direction: "top",
                    offset: [0, -24],
                });

                return marker;
            },
        }).addTo(this.map);

        this.amenityCache?.remove();
        this.amenityCache = layer;
    }

    private async updateAffectedStructures() {
        if(this.getView().zoom < STRUCTURE_ZOOM_LEVEL) {
            this.affectedStructureCache?.remove();
            return;
        }

        if(!this.showStructures) {
            this.affectedStructureCache?.remove();
            return;
        }

        const affectedStructuresUrl = this.app.selectedDisasterZone?.affectedStructuresUrl;
        if(!affectedStructuresUrl) {
            return;
        }

        const bounds = this.getBounds();
        const features = await fetchGeoJSON(affectedStructuresUrl, bounds, STRUCTURE_LIMIT);

        const layer = L.geoJSON(features, {
            style: {
                color: this.$vuetify.theme.currentTheme.error?.toString(),
            },
        }).addTo(this.map);

        this.affectedStructureCache?.remove();
        this.affectedStructureCache = layer;
    }

    private async updateUnaffectedStructures() {
        if(this.getView().zoom < STRUCTURE_ZOOM_LEVEL) {
            this.unaffectedStructureCache?.remove();
            return;
        }

        if(!this.showStructures) {
            this.unaffectedStructureCache?.remove();
            return;
        }

        const unaffectedStructuresUrl = this.app.selectedDisasterZone?.unaffectedStructuresUrl;
        if(!unaffectedStructuresUrl) {
            return;
        }

        const bounds = this.getBounds();
        const features = await fetchGeoJSON(unaffectedStructuresUrl, bounds, STRUCTURE_LIMIT);

        const layer = L.geoJSON(features, {
            style: {
                color: this.$vuetify.theme.currentTheme.success?.toString(),
            },
        }).addTo(this.map);

        this.unaffectedStructureCache?.remove();
        this.unaffectedStructureCache = layer;
    }

    private async updateHeatmap() {
        this.heatmapLayer?.remove();

        if(!this.showHeatmap) {
            return;
        }

        const heatmapUrl = this.app.selectedDisasterZone?.heatmapUrl;
        if(!heatmapUrl) {
            return;
        }

        const heatmap = await fetchHeatmap(heatmapUrl);
        this.heatmapLayer = (L as any).heatLayer(heatmap, {
            radius: 20,
            minOpacity: 0.7,
        }).addTo(this.map);
    }

    private onViewChanged() {
        this.updateRoute();

        this.updateAmenities();
        this.updateAffectedStructures();
        this.updateUnaffectedStructures();
    }

    private onToggleLayers() {
        if(this.visibleLayer === "none") {
            this.visibleLayer = "before";
        } else if(this.visibleLayer === "before") {
            this.visibleLayer = "after";
        } else {
            this.visibleLayer = "none";
        }
    }

    private onToggleHeatmap() {
        this.showHeatmap = !this.showHeatmap;
        this.updateHeatmap();
    }

    private onToggleAmenities() {
        this.showAmenities = !this.showAmenities;

        if(this.showAmenities) {
            this.setView({
                ...this.getView(),
                zoom: Math.max(AMENITY_ZOOM_LEVEL, this.map.getZoom()),
                fly: true,
            });
        }

        this.updateAmenities();
    }

    private onToggleDamagePolygons() {
        this.showStructures = !this.showStructures;

        if(this.showStructures) {
            this.setView({
                ...this.getView(),
                zoom: Math.max(STRUCTURE_ZOOM_LEVEL, this.map.getZoom()),
                fly: true,
            });
        }

        this.updateAffectedStructures();
        this.updateUnaffectedStructures();
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

    @Watch("app.selectedDisasterZone", {immediate: true})
    private async onDisasterZoneSelected(disasterZone: IDisasterZone | null) {
        await this.$nextTick();

        this.beforeLayer?.remove();
        this.afterLayer?.remove();

        this.beforeLayer = null;
        this.afterLayer = null;

        if(!disasterZone) {
            return;
        }

        if(disasterZone.beforeLayer) {
            this.beforeLayer = this.beforeLayer = L.tileLayer(disasterZone.beforeLayer.urlTemplate, {
                attribution: disasterZone.beforeLayer.attributionHtml,
            });
        }

        if(disasterZone.afterLayer) {
            this.afterLayer = this.afterLayer = L.tileLayer(disasterZone.afterLayer.urlTemplate, {
                attribution: disasterZone.afterLayer.attributionHtml,
            });
        }

        this.updateHeatmap().then();
        this.onVisibleLayerChanged();

        this.setView({
            center: disasterZone.center,
            zoom: 10,
            fly: true,
        });
    }

    @Watch("visibleLayer", {immediate: true})
    private onVisibleLayerChanged() {
        this.beforeLayer?.remove();
        this.afterLayer?.remove();

        if(this.visibleLayer === "before") {
            this.beforeLayer?.addTo(this.map);
        } else if(this.visibleLayer === "after") {
            this.afterLayer?.addTo(this.map);
        }
    }

    beforeRouteUpdate(to: Route, from: Route, next: NavigationGuardNext): void {
        next(vm => (vm as HomeView).navigateToRouteView());
    }

    async mounted(): Promise<void> {
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

        this.visibleLayer = "before";

        this.map.on("moveend", () => this.onViewChanged());
        this.map.on("zoomend", () => this.onViewChanged());

        this.navigateToRouteView();

        try {
            const disasterZones = await fetchDisasterZones();
            this.app.setDisasterZones(disasterZones);
            this.app.setDefaultDisasterZone();
        } finally {
            this.pending = false;
        }
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
    width: 100px;

    text-align: end;
}

.map-option-inactive {
    opacity: 0.6;
}

</style>
