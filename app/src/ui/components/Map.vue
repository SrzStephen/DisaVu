<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <div ref="map"
         class="map" />
</template>

<!--suppress JSMethodCanBeStatic, JSUnusedGlobalSymbols -->
<script lang="ts">

import * as L from "leaflet";

import {
    Component,
    Ref,
    Vue,
} from "vue-property-decorator";

import { ILatLng } from "@/models";

export interface IViewOptions {
    center: ILatLng;
    zoom: number;
    fly?: boolean;
}

@Component
export default class Map extends Vue {
    @Ref("map") private mapRef!: HTMLElement;

    private map!: L.Map;

    getView(): IViewOptions {
        return {
            center: this.map.getCenter(),
            zoom: this.map.getZoom(),
        };
    }

    setView(options: Partial<IViewOptions>): void {
        const center = options.center || this.getView().center;
        const zoom = options.zoom || this.getView().zoom;

        if(options.fly) {
            this.map.flyTo(center, zoom);
        } else {
            this.map.setView(center, zoom);
        }
    }

    private onMove() {
        this.$emit("move");
    }

    private onMoveEnd() {
        this.$emit("view-change");
    }

    private onZoom() {
        this.$emit("zoom");
    }

    private onZoomEnd() {
        this.$emit("view-change");
    }

    mounted(): void {
        this.map = L.map(this.mapRef).setView([-31.9658588, 115.8871002], 12);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors",
        }).addTo(this.map);

        this.map.on("move", () => this.onMove());
        this.map.on("moveend", () => this.onMoveEnd());

        this.map.on("zoom", () => this.onZoom());
        this.map.on("zoomend", () => this.onZoomEnd());
    }

    beforeDestroy(): void {
        this.map.remove();
    }
}

</script>

<style lang="scss" scoped>

.map {
    display: block;
    width: 100%;
    //height: 400px;
    height: 100%;
}

</style>
