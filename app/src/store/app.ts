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

import {} from "@/models";

VuexModuleDecoratorsConfig.rawError = true;

@Module({
    store,
    dynamic: true,
    namespaced: true,
    name: "app",
})
export class AppModule extends VuexModule {
    @Mutation
    initializeStore(): void {
        //
    }

    @Mutation
    uninitializeStore(): void {
        //
    }
}
