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

                    <div class="ms-2"
                         style="font-size: 20px">
                        DisaVu
                    </div>
                </v-btn>
            </v-toolbar-items>

            <v-spacer />

            <v-select dense solo-inverted flat hide-details return-object
                      class="mx-2"
                      style="max-width: 300px"
                      item-value="id"
                      item-text="name"
                      :items="app.disasterZones"
                      :value="app.selectedDisasterZone"
                      @change="onSelectDisasterZone" />

            <v-btn icon
                   :disabled="!app.selectedDisasterZone"
                   @click="onSelectDisasterZone(app.selectedDisasterZone)">
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
                    <v-list-item href="https://twitter.com/RicoBeti"
                                 target="_blank">
                        <v-list-item-icon>
                            <v-icon color="#1da1f2">
                                mdi-twitter
                            </v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title>
                                @RicoBeti
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>

                    <v-list-item href="https://twitter.com/Phtevem"
                                 target="_blank">
                        <v-list-item-icon>
                            <v-icon color="#1da1f2">
                                mdi-twitter
                            </v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title>
                                @Phtevem
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>

                    <v-list-item href="https://github.com/SrzStephen/BuildingDamage"
                                 target="_blank">
                        <v-list-item-icon>
                            <v-icon color="#333">
                                mdi-github
                            </v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title>
                                Source Code
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

import { IDisasterZone } from "@/models";

@Component
export default class App extends Vue {
    private readonly app = getModule(AppModule);

    private onSelectDisasterZone(disasterZone: IDisasterZone) {
        this.app.setSelectedDisasterZone(null);
        this.app.setSelectedDisasterZone(disasterZone);
    }

    mounted(): void {
        this.app.initializeStore();
    }

    beforeDestroy(): void {
        this.app.uninitializeStore();
    }
}

</script>
