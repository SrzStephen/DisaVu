/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use std::collections::HashMap;
use std::path::Path;

use geojson::Feature;

use crate::kdbush::KDBush;

pub struct GeoIndex {
    index: KDBush,
    data: HashMap<usize, Feature>,
}

impl std::fmt::Debug for GeoIndex {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "[GeoIndex {} points, {} features]",
            self.index.len(),
            self.data.len()
        )
    }
}

impl GeoIndex {
    pub fn query_within_viewport(
        &self,
        ne_lat: f64,
        ne_lng: f64,
        sw_lat: f64,
        sw_lng: f64,
        limit: usize,
    ) -> Vec<&Feature> {
        let mut unique_features = HashMap::new();
        self.index
            .range_with_predicate(sw_lng, sw_lat, ne_lng, ne_lat, |id| {
                unique_features
                    .entry(id)
                    .or_insert(self.data.get(&id).unwrap());

                unique_features.len() < limit
            });

        unique_features
            .values()
            .take(limit)
            .cloned()
            .collect()
    }
}

const DEFAULT_NODE_SIZE: u8 = 64;

#[derive(Debug)]
pub struct GeoIndexBuilder {
    geo_index: GeoIndex,
}

impl GeoIndexBuilder {
    pub fn new() -> Self {
        GeoIndexBuilder {
            geo_index: GeoIndex {
                index: KDBush::new(0, DEFAULT_NODE_SIZE),
                data: HashMap::new(),
            },
        }
    }

    pub fn add_features_from_file<P: AsRef<Path>>(self, _path: P) -> Self {
        // TODO: IMPLEMENT.
        self
    }

    pub fn build(mut self) -> GeoIndex {
        self.geo_index.index.build_index();
        self.geo_index
    }
}
