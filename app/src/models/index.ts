/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

export type Opaque<K, T> = T & { __TYPE__: K };
export type Uuid = Opaque<"Uuid", string>;

export interface ILatLng {
    lat: number;
    lng: number;
}

export interface ILayerData {
    urlTemplate: string;
    attributionHtml: string;
}

export interface IDisasterZone {
    id: Uuid;
    name: string;
    center: {
        lat: number;
        lng: number;
        zoom: number;
    };
    beforeLayer: ILayerData | null;
    afterLayer: ILayerData | null;
    amenitiesUrl: string | null;
    affectedStructuresUrl: string | null;
    unaffectedStructuresUrl: string | null;
    heatmapUrl: string | null;
}
