<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-container fluid fill-height
                 class="pa-0">
        <Map ref="map"
             style="z-index: 0"
             @view-change="onViewChanged" />

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

import { IDisasterZone } from "@/models";

import Map, { IViewOptions } from "@/ui/components/Map.vue";

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

@Component({
    components: {
        Map,
    },
})
export default class HomeView extends Vue {
    private readonly app = getModule(AppModule);

    @Ref("map") private map!: Map;

    private showAfterLayer = true;
    private showHeatmap = false;
    private showDamagePolygons = false;

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
                this.map.setView(view);
            }
        }
    }

    private onViewChanged() {
        this.updateRoute(this.map.getView());
    }

    private onToggleLayers() {
        this.showAfterLayer = !this.showAfterLayer;
        this.map.visibleLayers(this.showAfterLayer ? "after" : "before");
    }

    private onToggleHeatmap() {
        this.showHeatmap = !this.showHeatmap;
    }

    private onToggleDamagePolygons() {
        this.showDamagePolygons = !this.showDamagePolygons;
    }

    @Watch("app.selectedDisasterZone")
    onDisasterZoneSelected(disasterZone: IDisasterZone | null): void {
        if(disasterZone) {
            this.map.setView({
                center: disasterZone.center,
                zoom: 10,
                fly: true,
            });
        }
    }

    mounted(): void {
        this.navigateToRouteView();
    }

    beforeRouteUpdate(to: Route, from: Route, next: NavigationGuardNext): void {
        next(vm => (vm as HomeView).navigateToRouteView());
    }
}

</script>

<style lang="scss" scoped>

$side-offset: 20px;

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
