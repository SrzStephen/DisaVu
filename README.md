
![DisaVu](docs/disavu.png)

[![DisaVu](https://img.shields.io/badge/app-disavu-00897b.svg?style=for-the-badge)](https://disavu.silentbyte.com)&nbsp;
[![Version](https://img.shields.io/badge/version-1.0-05A5CC.svg?style=for-the-badge)](https://disavu.silentbyte.com)&nbsp;
[![Status](https://img.shields.io/badge/status-live-00B20E.svg?style=for-the-badge)](https://disavu.silentbyte.com)


# DisaVu Disaster Response System

DisaVu is a disaster response solution that helps direct relief resources to where they are needed most using a sophisticated machine learning approach. This repository represents our submission for the [AWS Disaster Response Hackathon Powered By Amazon SageMaker Studio Lab](https://awsdisasterresponse.devpost.com/).


## Inspiration

Natural disasters such as hurricanes, floods, or wildfires, can occur suddenly and have a devastating effect on the affected communities. Due to environmental changes induced by climate change, it is possible that the frequency of disasters may increase. It is thus of vital importance that communities are well prepared and that disaster response teams are optimally equipped with tools that make the allocation of limited resources as efficient and effective as possible.

*Essentially, DisaVu is a disaster response solution that helps allocate relief resources to where they are needed most using a sophisticated machine learning approach that is able to detect the extent of damage caused by natural disasters based on satellite images.*

Furthermore, three challenges from the [inspiration page on Devpost](https://awsdisasterresponse.devpost.com/details/inspiration) steered us into a more specific direction:

1. SPB: How might we determine the extent of damage to individual homes in a given disaster-impacted area?

2. ADB: How might we determine the condition of critical infrastructure and prioritise recovery needs after a disaster impacts a given area?

3. NASA ESDS: How can we help society respond to natural disasters using Earth Remote Sensing Observations?


## What it does

### The General Concept

Before getting into the technical details, here is a summary of the inference stages:

1. Get a GEOTIFF of before and after the natural disaster.

2. Feed the before image into the first model to generate building footproint longitude/latitude polygons.

3. Cut out only those polygons from the after natural disaster image to figure out if they are damaged or not.

4. Show those results on a map to help establish where has been impacted and where has been impacted the most.


**TODO: RICO IMAGE HERE**


## How we built it

### Models

TODO: Models can be trained using the notebook in a...


#### Model 1: Building detection and masking from satellite imagery

For building detection and masking, we used UNet architecture using [FastAIs dynamic UNet builder](https://docs.fast.ai/vision.models.unet.html) to perform the semantic segmentation to go from a satellite image of a house to a mask of the buildings.

The loss function we chose is a combination of [Focal loss](https://arxiv.org/pdf/1708.02002.pdf) and [Dice loss](https://pubmed.ncbi.nlm.nih.gov/34104926/) which [seems to perform well when there is a high input and output balance in segmentation tasks](https://arxiv.org/pdf/1805.02798.pdf).


#### Training Data

For training data we used data generated as part of the [SpaceNet2 Challenge](https://spacenet.ai/spacenet-buildings-dataset-v2),which provides labelled data for 151k buildings in Las Vegas, 23k in Paris, 92K in Shanghai and 35K in Khartoum.

This data can be downloaded from the Registry of Open Data on AWS. It's worth pointing out that there is both a public test set and a public train set, we elected only to use the train set and held back a percentage of the tiles for validation purposes.

```bash
aws s3 cp s3://spacenet-dataset/AOIs/AOI_2_Vegas/misc/AOI_2_Vegas_Train.tar.gz .
aws s3 cp s3://spacenet-dataset/AOIs/AOI_2_Vegas/misc/AOI_2_Vegas_Test_public.tar.gz
```

This dataset is licenced under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).


##### Data Prep

We used an open source Python package called [Solaris](https://solaris.readthedocs.io/en/latest/index.html) to prepare our training data by generating three different masks for the data targets, contact points between buildings, edges of buildings and interior of buildings.

This approach seems to have been successful by the [winners of the SpaceNet2 Challenge](https://github.com/SpaceNetChallenge/BuildingDetectors_Round2) and we found without this step, the bounds between buildings became very difficult to train on.

![Mask explaination](docs/data_prep_mask.png)


##### Results

![Docs](docs/target_prediction.png)

Probably worth doing a few things for this section:

1. Include Tensorboard output of training process because that's always neat

2. Focus on one good and one bad image from the set

3. Include a foreground_acc metric (non background accuracy) so we have something

4. Make sure to show valid vs train loss (assuming tensorboard)


### Model 2: Damage Detection


#### Training Data

We use the [XView2 dataset](https://xview2.org/dataset) which is described on [arxiv](https://arxiv.org/abs/1911.09296).

This data is available under a [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) licence.

This dataset was generated from [Maxar Open Data Program](https://www.digitalglobe.com/ecosystem/open-data).

For our purposes we only focused on Hurricanes, Monsoons, Tornado's. which means we have data from

** TODO: Check Monsoon, Get Countries
* Hurricane Michael Oct 7-16, 2018
* Hurricane Florence Sep 10-19, 2018
* Hurricane Harvey Aug 17 - Sep 2, 2017
* Hurricane Matthew Sep 28 - Oct 10, 2016
* Monsoon in Nepal, India, Bangladesh Jul - Sep, 2017
* Moore, OK Tornado May 20, 2013
* Tuscaloosa, AL Tornado Apr 27, 2011
* Joplin, MO Tornado May 22, 2011


#### Data Prep

Take the image, segment it out to only contain that building.
![](docs/damaged_undamaged.png)



#### Results

TODO: Recall, precision, accuracy tensorboard, show on map


#### Inference

Because the point of ML projects is to be useful with the real world, rather than perfectly curated ideal datasets, the inference stage uses Pr and Post disaster GeoTIFFs from [Maxars Open Data Program](https://registry.opendata.aws/digital-globe-open-data/).

It would be possible to use alternate sources like [Sentinel-2](https://registry.opendata.aws/sentinel-2/) flyovers, but the Maxxar dataset has the advantage of being very clear about which area and which dates are pre/post disaster.


Two GeoTIFFs are trimmed into areas of interest where they both intersect, and smaller tiles of images are generated (You'd quickly run out of ram trying to run a ML model against a single 1GB+ GeoTIFF), building footprints are identified by the first model, then those footprints are cut out from the second image, rated for damaged or not damaged, and then the resulting polygons are saved as a JSON object in the form of.


### Note to stephen, now geojson format so that it'll work with tile server
```json
{
  "TODO:"TODO""
}
```
This is then used by the frontend



### XView2 Feature Extractor

The purpose of XView2 Feature Extractor is to extract the required features from the XView2 Data Set. Essentially, the program takes labels (polygon data) and satellite images as input and then extracts and preprocesses image data for each label (polygon) and stores the results in output images. Those output images are then subsequently for training the machine learning part of the DisaVu system.

TODO: Explain in more detail.

XView2 Feature Extractor has been built using: [Rust](https://www.rust-lang.org).

[More details are available here.](./xview2_feature_extractor/README.md)


### GeoServ

GeoServ is a custom-built solution to serve GeoJSON and heatmap data for use in DisaVu. It supports high-performance geospatial queries using a specific type of [K-d tree](https://en.wikipedia.org/wiki/K-d_tree) to build an index that is optimized for static data. It used used for visualizations in the front-end and is able to serve polygon and point GeoJSON data, as well as generate heatmaps for them.

GeoServ has been built using: [Rust](https://www.rust-lang.org), [Actix Web](https://actix.rs).

[More details are available here.](./geoserv/README.md)


### Web App / Map

The web app is the front-end that is intended to be used by a disaster response team to coordinate actions and allocate resources. The main feature of the app is a dynamic map that visualizes disaster zones by...

- ...showing before/after satellite images,
- ...highlighting buildings/structures outlines (polygons),
- ...giving an indication if structures have been damaged,
- ...rendering a heatmap to show where damage clusters are,
- ...showing relevant amenities such as schools, universities, hospitals, fire stations, police stations, and more.

The app has been built using: [TypeScript](https://www.typescriptlang.org), [VueJs](https://vuejs.org), [Leaflet](https://leafletjs.com).

[More details are available here.](./app/README.md)


## Additional

This could further be augmented by data from the [Open AI Tanzania Building Footprint Segmentation Challenge Dataset](https://competitions.codalab.org/competitions/20100#learn_the_details) to include another geographic region, but we avoided doing this to reduce the complexity of the notebook.

TODO:
The datset we use for building damage detection has more cases than just hurricanes

The dataset we use for building detection has levels of damage


We've found [This repo](https://github.com/robmarkcole/satellite-image-deep-learning) to be a good source of data sources and ideas.


https://aws.amazon.com/blogs/machine-learning/building-training-and-deploying-fastai-models-with-amazon-sagemaker/


https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lab-use-manage.html
https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lab-use-external.html#studio-lab-use-external-add-button



## Challenges we ran into

* JPG compressions on masks are... not good.
* Conda, as someone who's more used to pip and pyenv, Conda is great, especially for solving issues of packages needing other dependencies that can be a pain to install like GDAL.


### Limitations

#### Data

We stripped down the data used for this for two reasons

1. To reduce sizes

2. Because while it is posible to use the full 100GB datasets, it's not possible to do this with the 15GB limit on sagemaker studio, for this sort of thing you'd want the full blown sagemaker.


#### Notebook Complexity

Putting all of the code in one block was extremly painful to read, we ended up breaking some code out into their own modules (preprocessing, postprocessing).


## Accomplishments that we're proud of

TODO.


## What we learned

- We had the chance to look into how massive amounts of geospatial data can and should be stored, processed, an queried.
- TODO.


## What's next for DisaVu

TODO.
