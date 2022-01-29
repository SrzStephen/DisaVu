/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use std::collections::HashMap;
use std::sync::Arc;

use actix_web::{
    web,
    HttpResponse,
    Responder,
    Result as ActixResult,
};
use serde::Deserialize;

use crate::geodata::GeoIndex;

pub type GeoIndexesData = Arc<HashMap<(String, String), GeoIndex>>;

#[derive(Deserialize, Debug)]
pub struct ViewportQueryParams {
    ne_lat: f64,
    ne_lng: f64,
    sw_lat: f64,
    sw_lng: f64,
    limit: Option<usize>,
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

pub async fn geo_route(
    geo_index: web::Data<GeoIndexesData>,
    web::Path((group, name)): web::Path<(String, String)>,
    viewport: web::Query<ViewportQueryParams>,
) -> ActixResult<impl Responder> {
    let limit = viewport.limit.unwrap_or(100).min(10_000);
    let features = geo_index
        .get(&(group, name))
        .ok_or(HttpResponse::NotFound())?
        .query_within_viewport(
            viewport.ne_lat,
            viewport.ne_lng,
            viewport.sw_lat,
            viewport.sw_lng,
            limit,
        );

    Ok(HttpResponse::Ok().json(&features))
}
pub async fn geo_heatmap_route(
    geo_index: web::Data<GeoIndexesData>,
    web::Path((group, name)): web::Path<(String, String)>,
) -> ActixResult<impl Responder> {
    let heatmap = geo_index
        .get(&(group, name))
        .ok_or(HttpResponse::NotFound())?
        .heatmap();

    Ok(HttpResponse::Ok().json(&heatmap))
}
