<!--
    DISASTER RESPONSE APP
    Copyright (c) 2021 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-container fluid fill-height
                 class="pa-0">
        <Map ref="map"
             @view-change="onViewChanged" />
    </v-container>
</template>

<!--suppress JSMethodCanBeStatic, JSUnusedGlobalSymbols -->
<script lang="ts">

import {
    Component,
    Ref,
    Vue,
} from "vue-property-decorator";

import { getModule } from "vuex-module-decorators";
import { AppModule } from "@/store/app";

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

    private updateRoute(view: IViewOptions) {
        const latitude = view.center.lat.toFixed(7);
        const longitude = view.center.lng.toFixed(7);
        const zoom = view.zoom.toFixed(0);

        const options = `@${latitude},${longitude},${zoom}z`;
        if(this.$route.params.options !== options) {
            this.$router.replace({
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

    mounted(): void {
        this.navigateToRouteView();
    }

    beforeRouteUpdate(): void {
        this.navigateToRouteView();
    }
}

</script>
