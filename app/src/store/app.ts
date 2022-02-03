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

import { IDisasterZone } from "@/models";

VuexModuleDecoratorsConfig.rawError = true;

@Module({
    store,
    dynamic: true,
    namespaced: true,
    name: "app",
})
export class AppModule extends VuexModule {
    disasterZones: IDisasterZone[] = [];

    selectedDisasterZone: IDisasterZone | null = null;

    @Mutation
    initializeStore(): void {
        //
    }

    @Mutation
    uninitializeStore(): void {
        //
    }

    @Mutation
    setDisasterZones(disasterZones: IDisasterZone[]): void {
        this.disasterZones = disasterZones;
    }

    @Mutation
    setSelectedDisasterZone(disasterZone: IDisasterZone | null): void {
        this.selectedDisasterZone = disasterZone;

        if(disasterZone) {
            localStorage.setItem("selected-disaster-zone", disasterZone.id);
        } else {
            localStorage.removeItem("selected-disaster-zone");
        }
    }

    @Mutation
    setDefaultDisasterZone(): void {
        const id = localStorage.getItem("selected-disaster-zone");
        const disasterZone = id
            ? this.disasterZones.find(dz => dz.id === id) || this.disasterZones[0] || null
            : this.disasterZones[0];

        this.selectedDisasterZone = disasterZone;

        if(disasterZone) {
            localStorage.setItem("selected-disaster-zone", disasterZone.id);
        } else {
            localStorage.removeItem("selected-disaster-zone");
        }
    }
}
