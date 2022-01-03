/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";

import HomeView from "@/ui/views/HomeView.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
    {
        path: "/:options(@[\\-0-9\\.\\,]+z)?",
        name: "Home",
        component: HomeView,
    },
];

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
});

export default router;
