/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

import {
    config as VuexModuleDecoratorsConfig,
    Module,
    Mutation,
    VuexModule,
} from "vuex-module-decorators";

import store from "@/store";

import {
    IDisasterZone,
    Uuid,
} from "@/models";

VuexModuleDecoratorsConfig.rawError = true;

@Module({
    store,
    dynamic: true,
    namespaced: true,
    name: "app",
})
export class AppModule extends VuexModule {
    disasterZones: IDisasterZone[] = [
        {
            id: "83c6f91d-7c3a-4a43-83f3-9f3541dc6441" as Uuid,
            name: "Oman",
            center: {
                lat: 23.5909276,
                lng: 58.5182752,
                zoom: 10,
            },
            beforeLayer: {
                urlTemplate: "http://159.223.58.255:5000/rgb/before/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]",
                attributionHtml: "&copy; <a href=\\\"https://www.maxar.com/open-data\\\">Maxar</a>",
            },
            afterLayer: {
                urlTemplate: "http://159.223.58.255:5000/rgb/after/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]",
                attributionHtml: "&copy; <a href=\\\"https://www.maxar.com/open-data\\\">Maxar</a>",
            },
            amenitiesUrl: null,
            affectedStructuresUrl: null,
            unaffectedStructuresUrl: null,
            heatmapUrl: null,
        },
        {
            id: "886cc6b1-2951-4e7d-ad94-dedff09e22ef" as Uuid,
            name: "Hurricane Harvey",
            center: {
                lat: 29.76927046175237,
                lng: -95.48923259304139,
                zoom: 10,
            },
            beforeLayer: null,
            afterLayer: null,
            amenitiesUrl: null,
            affectedStructuresUrl: null,
            unaffectedStructuresUrl: null,
            heatmapUrl: null,
        },
        {
            id: "e2f796fe-8ec6-4c2d-b8b6-c6c4597ced16" as Uuid,
            name: "Palu Tsunami",
            center: {
                lat: -0.7902744312373666,
                lng: 119.7995020190507,
                zoom: 10,
            },
            beforeLayer: null,
            afterLayer: null,
            amenitiesUrl: null,
            affectedStructuresUrl: null,
            unaffectedStructuresUrl: null,
            heatmapUrl: null,
        },
        {
            id: "d6be9a72-99d6-4c56-bd7f-f1dba4ba413a" as Uuid,
            name: "Vegas",
            center: {
                lat: 36.1909007,
                lng: -115.1270185,
                zoom: 10,
            },
            beforeLayer: null,
            afterLayer: null,
            amenitiesUrl: "http://127.0.0.1:8088/geo/vegas/amenities",
            affectedStructuresUrl: "http://127.0.0.1:8088/geo/vegas/structures-affected",
            unaffectedStructuresUrl: "http://127.0.0.1:8088/geo/vegas/structures-unaffected",
            heatmapUrl: "http://127.0.0.1:8088/geo/vegas/structures-affected/heatmap",
        },
    ];

    selectedDisasterZone: IDisasterZone | null = this.defaultDisasterZone();

    private defaultDisasterZone(): IDisasterZone | null {
        const id = localStorage.getItem("selected-disaster-zone");
        if(!id) {
            return this.disasterZones[0];
        }

        return this.disasterZones.find(dz => dz.id === id) || this.disasterZones[0] || null;
    }

    @Mutation
    initializeStore(): void {
        //
    }

    @Mutation
    uninitializeStore(): void {
        //
    }

    @Mutation
    setSelectedDisaster(disasterZone: IDisasterZone | null): void {
        this.selectedDisasterZone = disasterZone;

        if(disasterZone) {
            localStorage.setItem("selected-disaster-zone", disasterZone.id);
        } else {
            localStorage.removeItem("selected-disaster-zone");
        }
    }
}
