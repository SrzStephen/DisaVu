<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-app>
        <v-app-bar app dark
                   color="primary">
            <v-toolbar-items>
                <v-btn text large>
                    <v-icon large left>
                        mdi-handshake
                    </v-icon>

                    <div class="ms-2 text-uppercase">
                        Disaster Map
                    </div>
                </v-btn>
            </v-toolbar-items>

            <v-spacer />

            <v-select dense solo-inverted flat hide-details return-object
                      class="mx-2"
                      style="max-width: 300px"
                      item-value="id"
                      item-text="name"
                      :items="app.disasters"
                      :value="app.selectedDisaster"
                      @change="onSelectDisaster" />

            <v-btn icon
                   :disabled="!app.selectedDisaster"
                   @click="onSelectDisaster(app.selectedDisaster)">
                <v-icon>mdi-navigation-outline</v-icon>
            </v-btn>

            <v-menu left bottom
                    nudge-bottom="50"
                    :close-on-content-click="false">
                <template v-slot:activator="{ on }">
                    <v-btn icon
                           v-on="on">
                        <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                </template>

                <v-list min-width="200">
                    <v-list-item>
                        <v-list-item-icon>
                            <v-icon>mdi-logout-variant</v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title>
                                Log Out
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </v-list>
            </v-menu>
        </v-app-bar>

        <v-main>
            <router-view />
        </v-main>
    </v-app>
</template>

<!--suppress JSMethodCanBeStatic, JSUnusedGlobalSymbols -->
<script lang="ts">

import {
    Component,
    Vue,
} from "vue-property-decorator";

import { getModule } from "vuex-module-decorators";
import { AppModule } from "@/store/app";

import { IDisaster } from "@/models";

@Component
export default class App extends Vue {
    private readonly app = getModule(AppModule);

    private onSelectDisaster(disaster: IDisaster) {
        this.app.setSelectedDisaster(null);
        this.app.setSelectedDisaster(disaster);
    }

    mounted(): void {
        this.app.initializeStore();
    }

    beforeDestroy(): void {
        this.app.uninitializeStore();
    }
}

</script>
