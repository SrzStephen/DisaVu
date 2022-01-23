/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use actix_web::{
    web,
    Responder,
    Result as ActixResult,
};
use serde::{
    Deserialize,
    Serialize,
};

#[derive(Deserialize, Debug)]
pub struct ViewportQueryParams {
    ne_lat: f64,
    ne_lng: f64,
    sw_lat: f64,
    sw_lng: f64,
}

impl std::fmt::Display for ViewportQueryParams {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "({} {}, {} {})",
            self.ne_lat, self.ne_lng, self.sw_lat, self.sw_lng
        )
    }
}

#[derive(Serialize, Debug)]
pub struct GeoDataResponse {
    //
}

pub async fn geo_data_route(
    web::Path((group, name)): web::Path<(String, String)>,
    viewport: web::Query<ViewportQueryParams>,
) -> ActixResult<impl Responder> {
    println!("{}/{} {}", group, name, viewport);
    Ok(web::Json(GeoDataResponse {}))
}
