# Composite

This microservice enables the creation of on-the-fly composites from a Geostore geometry.
Composites are returned either as url links to thumbnail and z/x/y web map tile assets,
or as a zip folder containing image assets.

The service returns visulized data for Landsat-8, and Sentinel-2 instruments. Band visulisations
can be given as argument, to visulise any bands of interest in RGB space. Digital Elevation Model (DEM)
images can also be returned with the `get_dem`=True flag.

Resolution can be controled via thumb_size. E.g. if a 500x500 pixel image is required, pass the argument
`thumb_size=[500,500]`.


## Examples

### URLs to thumbnail and WMT server

To obtain assets useful for driving 3D models:

```bash
wget --quiet \
  --method GET \
  --header 'Accept: */*' \
  --header 'Cache-Control: no-cache' \
  --header 'Host: api.skydipper.com' \
  --header 'Accept-Encoding: gzip, deflate' \
  --header 'Connection: keep-alive' \
  --header 'cache-control: no-cache' \
  --output-document \
  - 'https://api.skydipper.com/v1/composite-service/?geostore=c2a5f760a32447a4281a78705ed52c4c&instrument=landsat&thumb_size=[500,500]&get_dem=True&get_files=False&band_vizz={%27bands%27:%20[%27B4%27,%20%27B3%27,%20%27B2%27],%20%27min%27:%200,%20%27max%27:%200.4}&cloudscore_thresh=5&date_range=[2018-01-01,%202018-10-01]'

```


### Download of assets to drive 3D models

```bash
wget --quiet \
  --method GET \
  --header 'Accept: */*' \
  --header 'Cache-Control: no-cache' \
  --header 'Host: api.skydipper.com' \
  --header 'Accept-Encoding: gzip, deflate' \
  --header 'Connection: keep-alive' \
  --header 'cache-control: no-cache' \
  --output-document \
  - 'https://api.skydipper.com/v1/composite-service/?geostore=c2a5f760a32447a4281a78705ed52c4c&instrument=landsat&thumb_size=[500,500]&get_dem=True&get_files=True&band_vizz={%27bands%27:%20[%27B4%27,%20%27B3%27,%20%27B2%27],%20%27min%27:%200,%20%27max%27:%200.4}&cloudscore_thresh=5&date_range=[2018-01-01,%202018-10-01]'
```
