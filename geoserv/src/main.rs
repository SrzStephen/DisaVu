/*
 * GEOSERV
 * Copyright (c) 2022 SilentByte <https://silentbyte.com/>
 */

use actix_web::{
    web,
    App,
    HttpServer,
    Responder,
};
use argh::FromArgs;
use serde::{
    Deserialize,
    Serialize,
};

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

#[derive(Deserialize, Debug)]
struct ViewportQueryParams {
    ne_lat: f64,
    ne_lng: f64,
    sw_lat: f64,
    sw_lng: f64,
}

impl std::fmt::Display for ViewportQueryParams {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{} {}, {} {}",
            self.ne_lat, self.ne_lng, self.sw_lat, self.sw_lng
        )
    }
}

#[derive(Serialize, Debug)]
struct GeoDataResponse {
    //
}

async fn geo_data_route(
    web::Path((group, name)): web::Path<(String, String)>,
    viewport: web::Query<ViewportQueryParams>,
) -> actix_web::Result<impl Responder> {
    println!("{}/{} {}", group, name, viewport);
    Ok(web::Json(GeoDataResponse {}))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
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

    HttpServer::new(move || {
        App::new()
            .service(web::resource("/data/{group}/{name}").route(web::get().to(geo_data_route)))
    })
    .bind(bind_address)?
    .run()
    .await
}
