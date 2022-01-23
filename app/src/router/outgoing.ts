/*
 * DISASTER RESPONSE APP
 * Copyright (c) 2021 SilentByte <https://silentbyte.com/>
 */

export function publicUrl(...path: string[]): string {
    const fullPath = path.map(p => p.replace(/^\//, "").replace(/\/$/, "")).join("/");
    return `${process.env.VUE_APP_ABSOLUTE_URL || ""}${fullPath}`;
}
