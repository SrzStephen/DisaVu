/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

import Vue from "vue";

import App from "@/App.vue";
import router from "@/router";
import store from "@/store";
import vuetify from "@/plugins/vuetify";
import "@/plugins/vue-class-component";
import "@/plugins/leaflet";

import "@/styles/app.scss";

Vue.config.productionTip = false;

new Vue({
    router,
    store,
    vuetify,
    render: h => h(App),
}).$mount("#app");
