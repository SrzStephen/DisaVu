/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

use crate::kdbush::KDBush;

pub type GeoPoint = (f64, f64);

pub struct GeoIndex {
    index: KDBush,
    data: HashMap<usize, geojson::Feature>,
    heatmap: Vec<GeoPoint>,
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
    ) -> Vec<&geojson::Feature> {
        let mut unique_features = HashMap::new();
        self.index
            .range_with_predicate(sw_lat, sw_lng, ne_lat, ne_lng, |id| {
                unique_features
                    .entry(id)
                    .or_insert(self.data.get(&id).unwrap());

                unique_features.len() < limit
            });

        unique_features.values().take(limit).cloned().collect()
    }

    pub fn heatmap(&self) -> &[GeoPoint] {
        &self.heatmap
    }

    pub fn len(&self) -> usize {
        return self.data.len();
    }
}

const DEFAULT_NODE_SIZE: u8 = 64;

#[derive(Debug)]
pub struct GeoIndexBuilder {
    geo_index: GeoIndex,
    auto_index_counter: usize,
}

impl GeoIndexBuilder {
    pub fn new() -> Self {
        GeoIndexBuilder {
            geo_index: GeoIndex {
                index: KDBush::new(0, DEFAULT_NODE_SIZE),
                data: HashMap::new(),
                heatmap: Vec::new(),
            },
            auto_index_counter: 0,
        }
    }

    fn generate_id(&mut self) -> usize {
        let id = self.auto_index_counter;
        self.auto_index_counter += 1;
        id
    }

    fn add_bbox_points(&mut self, id: usize, bbox: &geojson::Bbox) {
        let mut center = (0f64, 0f64);
        let mut point_counter = 0;

        for point in bbox.chunks_exact(2) {
            self.geo_index.index.add_point(id, point[1], point[0]);

            center.0 += point[1];
            center.1 += point[0];
            point_counter += 1;
        }

        if point_counter > 0 {
            self.geo_index.heatmap.push((
                center.0 / point_counter as f64,
                center.1 / point_counter as f64,
            ));
        }
    }

    fn add_point_points(&mut self, id: usize, point: &geojson::PointType) {
        self.geo_index.index.add_point(id, point[1], point[0]);
        self.geo_index.heatmap.push((point[1], point[0]));
    }

    pub fn add_features_from_file(mut self, path: &Path) -> anyhow::Result<Self> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let geo_data: geojson::GeoJson = serde_json::from_reader(reader)?;

        let feature_collection = match geo_data {
            geojson::GeoJson::FeatureCollection(fc) => fc,
            _ => anyhow::bail!("{} does not contain a feature collection", path.display()),
        };

        for feature in feature_collection.features {
            let id = self.generate_id();

            if let Some(bbox) = &feature.bbox {
                self.add_bbox_points(id, &bbox);
            } else {
                match &feature.geometry.as_ref().unwrap().value {
                    geojson::Value::Point(point) => self.add_point_points(id, &point),
                    _ => anyhow::bail!("{} contains an unsupported feature type", path.display()),
                };
            }

            self.geo_index.data.insert(id, feature);
        }

        Ok(self)
    }

    pub fn build(mut self) -> GeoIndex {
        self.geo_index.index.build_index();
        self.geo_index
    }
}
