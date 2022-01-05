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

export interface IDisaster {
    id: Uuid;
    name: string;
    center: ILatLng;
}
