/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use std::sync::Arc;

use actix_web::{
    web,
    App,
    HttpServer,
};
use argh::FromArgs;
use geoserv::api;
use geoserv::geodata::GeoIndexBuilder;

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
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(
        env_logger::Env::default().filter_or(env_logger::DEFAULT_FILTER_ENV, "INFO"),
    );

    let args: Args = argh::from_env();
    let bind_address = format!("{}:{}", args.hostname, args.port);

    let geo_index = Arc::new(GeoIndexBuilder::new().build());

    log::info!(
        "Starting GeoServ on {}, serving {}",
        bind_address,
        args.data_dir
    );

    HttpServer::new(move || {
        App::new()
            .data(geo_index.clone())
            .service(
                web::resource("/data/{group}/{name}").route(web::get().to(api::geo_data_route)),
            )
    })
    .bind(bind_address)?
    .run()
    .await
}
