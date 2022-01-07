/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

import Vue from "vue";
import Vuetify from "vuetify/lib/framework";

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        options: {
            customProperties: true,
        },
        themes: {
            light: {
                primary: "#00897b",
                secondary: "#00695c",
                accent: "#e65100",
                error: "#ff5252",
                info: "#2196f3",
                success: "#4caf50",
                warning: "#ffc107",

                text: "#333",
                card: "#f9faff",
                disabled: "#ddd",
            },
        },
    },
});
