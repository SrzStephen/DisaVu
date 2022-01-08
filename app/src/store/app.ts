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
            },
        },
        {
            id: "886cc6b1-2951-4e7d-ad94-dedff09e22ef" as Uuid,
            name: "Hurricane Harvey",
            center: {
                lat: 29.76927046175237,
                lng: -95.48923259304139,
            },
        },
        {
            id: "e2f796fe-8ec6-4c2d-b8b6-c6c4597ced16" as Uuid,
            name: "Palu Tsunami",
            center: {
                lat: -0.7902744312373666,
                lng: 119.7995020190507,
            },
        },
    ];
    selectedDisasterZone: IDisasterZone | null = this.disasterZones[0];

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
    }
}
