/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use std::collections::HashMap;

use actix_cors::Cors;
use actix_web::middleware::{
    Compress,
    Logger,
};
use actix_web::{
    web,
    App,
    HttpServer,
};
use argh::FromArgs;
use geoserv::api;
use geoserv::api::GeoIndexesData;
use geoserv::geodata::GeoIndexBuilder;
use glob::glob;
use itertools::Itertools;

/// GeoServ.
#[derive(Debug, Clone, FromArgs)]
struct Args {
    /// the hostname on which the server will start listening.
    #[argh(option, default = r#""127.0.0.1".into()"#)]
    hostname: String,

    /// the images directory of the XView2 training data.
    #[argh(option, default = "8088")]
    port: u16,

    /// the directory where the GeoJSON files are located.
    #[argh(option)]
    data_dir: String,

    /// the number of worker threads to use.
    #[argh(option, default = "4")]
    workers: usize,
}

fn build_geo_indexes_from_directory_structure(args: &Args) -> anyhow::Result<GeoIndexesData> {
    let pattern = std::path::Path::new(&args.data_dir).join("*/*.geojson");
    let pattern = pattern
        .to_str()
        .ok_or(anyhow::anyhow!("Failed to expand glob pattern"))?
        .into();

    let mut geo_indexes = HashMap::new();

    for entry in glob(pattern)? {
        let entry = entry?;
        let path = entry.as_path();

        log::info!("Parsing {}", path.display());

        let group = path
            .parent()
            .unwrap()
            .file_name()
            .unwrap()
            .to_str()
            .unwrap()
            .to_owned();

        let name = path.file_stem().unwrap().to_str().unwrap().to_owned();

        geo_indexes.insert(
            (group, name),
            GeoIndexBuilder::new().add_features_from_file(path)?.build(),
        );
    }

    Ok(GeoIndexesData::new(geo_indexes))
}

#[actix_web::main]
async fn main() -> anyhow::Result<()> {
    env_logger::init_from_env(
        env_logger::Env::default().filter_or(env_logger::DEFAULT_FILTER_ENV, "INFO"),
    );

    let args: Args = argh::from_env();
    let bind_address = format!("{}:{}", args.hostname, args.port);

    log::info!(
        "Starting GeoServ on {}, serving {}",
        bind_address,
        args.data_dir
    );

    let geo_indexes_data = build_geo_indexes_from_directory_structure(&args)?;

    log::info!("The following geospatial data is available:");
    geo_indexes_data
        .iter()
        .map(|(k, v)| format!("{}/{}: {} feature(s)", k.0, k.1, v.len()))
        .sorted()
        .for_each(|e| log::info!("{}", e));

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .wrap(Cors::default().allow_any_origin())
            .wrap(Compress::default())
            .data(geo_indexes_data.clone())
            .service(web::resource("/geo/{group}/{name}").route(web::get().to(api::geo_route)))
            .service(
                web::resource("/geo/{group}/{name}/heatmap")
                    .route(web::get().to(api::geo_heatmap_route)),
            )
    })
    .workers(args.workers)
    .bind(bind_address)
    .map_err(|e| anyhow::anyhow!(e))?
    .run()
    .await?;

    Ok(())
}
