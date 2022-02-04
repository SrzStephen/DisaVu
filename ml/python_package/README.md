To simplify the code, a lot of the annoying preprocess code has been split into its own package which can be pip installed.


I dont actually know how to package conda stuff and it'll probably need to be conda because GDAL dependencies are a pain.

needed functions:

## Model 1
* Generate mask data
## Model 2
* Rico rust thing might need to be python :(


## Inference
* AOI between two tifs
* pix2geo
* mask2poly