"""Mock data fixtures for external API responses."""
import json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np

# GADM Mock Data
MOCK_GADM_GEODATAFRAME = gpd.GeoDataFrame(
    {
        'GID_0': ['USA', 'USA'],
        'NAME_0': ['United States', 'United States'],
        'GID_1': ['USA.1_1', 'USA.2_1'],
        'NAME_1': ['California', 'Texas'],
        'TYPE_1': ['State', 'State'],
    },
    geometry=[
        Polygon([(-124, 32), (-114, 32), (-114, 42), (-124, 42), (-124, 32)]),
        Polygon([(-106, 26), (-94, 26), (-94, 36), (-106, 36), (-106, 26)]),
    ],
    crs='EPSG:4326'
)

# GBIF Mock Data
MOCK_GBIF_SPECIES_INFO = {
    "usageKey": 2435099,
    "scientificName": "Puma concolor",
    "canonicalName": "Puma concolor",
    "rank": "SPECIES",
    "status": "ACCEPTED",
    "confidence": 99,
    "matchType": "EXACT",
    "kingdom": "Animalia",
    "phylum": "Chordata",
    "order": "Carnivora",
    "family": "Felidae",
    "genus": "Puma",
    "species": "Puma concolor",
    "kingdomKey": 1,
    "phylumKey": 44,
    "classKey": 359,
    "orderKey": 732,
    "familyKey": 9703,
    "genusKey": 2435098,
    "speciesKey": 2435099,
    "synonym": False,
    "class": "Mammalia"
}

MOCK_GBIF_OCCURRENCES = {
    "offset": 0,
    "limit": 100,
    "endOfRecords": False,
    "count": 1234567,
    "results": [
        {
            "key": 1234567890,
            "datasetKey": "50c9509d-22c7-4a22-a47d-8c48425ef4a7",
            "publishingOrgKey": "28eb1a3f-1c15-4a95-931a-4af90ecb574d",
            "publishingCountry": "US",
            "protocol": "DWC_ARCHIVE",
            "lastCrawled": "2024-01-15T10:30:00.000+0000",
            "lastParsed": "2024-01-15T10:35:00.000+0000",
            "crawlId": 123,
            "basisOfRecord": "HUMAN_OBSERVATION",
            "occurrenceStatus": "PRESENT",
            "taxonKey": 2435099,
            "kingdomKey": 1,
            "phylumKey": 44,
            "classKey": 359,
            "orderKey": 732,
            "familyKey": 9703,
            "genusKey": 2435098,
            "speciesKey": 2435099,
            "scientificName": "Puma concolor (Linnaeus, 1771)",
            "kingdom": "Animalia",
            "phylum": "Chordata",
            "order": "Carnivora",
            "family": "Felidae",
            "genus": "Puma",
            "species": "Puma concolor",
            "genericName": "Puma",
            "specificEpithet": "concolor",
            "taxonRank": "SPECIES",
            "decimalLatitude": 34.0522,
            "decimalLongitude": -118.2437,
            "coordinateUncertaintyInMeters": 100.0,
            "year": 2023,
            "month": 6,
            "day": 15,
            "eventDate": "2023-06-15T00:00:00",
            "issues": [],
            "lastInterpreted": "2024-01-15T10:35:00.000+0000",
            "license": "http://creativecommons.org/licenses/by/4.0/legalcode",
            "identifiers": [],
            "facts": [],
            "relations": [],
            "geodeticDatum": "WGS84",
            "class": "Mammalia",
            "countryCode": "US",
            "recordedByIDs": [],
            "identifiedByIDs": [],
            "country": "United States",
            "identifier": "urn:catalog:LACM:Mammals:12345",
            "institutionCode": "LACM",
            "collectionCode": "Mammals"
        }
    ],
    "facets": []
}

# STAC Mock Data (Planetary Computer)
MOCK_STAC_ITEM = {
    "type": "Feature",
    "stac_version": "1.0.0",
    "id": "S2A_MSIL2A_20240715T183921_R070_T11SLT_20240715T235352",
    "properties": {
        "datetime": "2024-07-15T18:39:21.024000Z",
        "platform": "sentinel-2a",
        "constellation": "sentinel-2",
        "instruments": ["msi"],
        "gsd": 10,
        "eo:cloud_cover": 5.23,
        "proj:epsg": 32611,
        "sentinel:product_id": "S2A_MSIL2A_20240715T183921_N0510_R070_T11SLT_20240715T235352",
        "sentinel:data_coverage": 100.0
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-119.0, 34.0],
            [-118.0, 34.0],
            [-118.0, 35.0],
            [-119.0, 35.0],
            [-119.0, 34.0]
        ]]
    },
    "links": [],
    "assets": {
        "B04": {
            "href": "https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/11/S/LT/2024/07/15/S2A_MSIL2A_20240715T183921_N0510_R070_T11SLT_20240715T235352.SAFE/GRANULE/L2A_T11SLT_A047123_20240715T184519/IMG_DATA/R10m/T11SLT_20240715T183921_B04_10m.jp2",
            "type": "image/jp2",
            "title": "Band 4 (red) - 10m",
            "eo:bands": [{"name": "B04", "common_name": "red", "center_wavelength": 0.665}],
            "gsd": 10,
            "proj:shape": [10980, 10980],
            "proj:transform": [10, 0, 600000, 0, -10, 3900000],
            "raster:bands": [{"nodata": 0, "data_type": "uint16", "spatial_resolution": 10}]
        },
        "B03": {
            "href": "https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/11/S/LT/2024/07/15/S2A_MSIL2A_20240715T183921_N0510_R070_T11SLT_20240715T235352.SAFE/GRANULE/L2A_T11SLT_A047123_20240715T184519/IMG_DATA/R10m/T11SLT_20240715T183921_B03_10m.jp2",
            "type": "image/jp2",
            "title": "Band 3 (green) - 10m",
            "eo:bands": [{"name": "B03", "common_name": "green", "center_wavelength": 0.56}],
            "gsd": 10,
            "proj:shape": [10980, 10980],
            "proj:transform": [10, 0, 600000, 0, -10, 3900000],
            "raster:bands": [{"nodata": 0, "data_type": "uint16", "spatial_resolution": 10}]
        },
        "B02": {
            "href": "https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/11/S/LT/2024/07/15/S2A_MSIL2A_20240715T183921_N0510_R070_T11SLT_20240715T235352.SAFE/GRANULE/L2A_T11SLT_A047123_20240715T184519/IMG_DATA/R10m/T11SLT_20240715T183921_B02_10m.jp2",
            "type": "image/jp2",
            "title": "Band 2 (blue) - 10m",
            "eo:bands": [{"name": "B02", "common_name": "blue", "center_wavelength": 0.49}],
            "gsd": 10,
            "proj:shape": [10980, 10980],
            "proj:transform": [10, 0, 600000, 0, -10, 3900000],
            "raster:bands": [{"nodata": 0, "data_type": "uint16", "spatial_resolution": 10}]
        },
        "B08": {
            "href": "https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/11/S/LT/2024/07/15/S2A_MSIL2A_20240715T183921_N0510_R070_T11SLT_20240715T235352.SAFE/GRANULE/L2A_T11SLT_A047123_20240715T184519/IMG_DATA/R10m/T11SLT_20240715T183921_B08_10m.jp2",
            "type": "image/jp2",
            "title": "Band 8 (nir) - 10m",
            "eo:bands": [{"name": "B08", "common_name": "nir", "center_wavelength": 0.842}],
            "gsd": 10,
            "proj:shape": [10980, 10980],
            "proj:transform": [10, 0, 600000, 0, -10, 3900000],
            "raster:bands": [{"nodata": 0, "data_type": "uint16", "spatial_resolution": 10}]
        }
    },
    "bbox": [-119.0, 34.0, -118.0, 35.0],
    "stac_extensions": [
        "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
        "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
    ],
    "collection": "sentinel-2-l2a"
}

MOCK_WORLDCOVER_ITEM = {
    "type": "Feature",
    "stac_version": "1.0.0",
    "id": "ESA_WorldCover_10m_2021_v200_N33W120_Map",
    "properties": {
        "datetime": "2021-01-01T00:00:00Z",
        "start_datetime": "2021-01-01T00:00:00Z",
        "end_datetime": "2021-12-31T23:59:59Z",
        "platform": "Sentinel-1 and Sentinel-2",
        "proj:epsg": 4326,
        "esa_worldcover:product_tile": "N33W120",
        "esa_worldcover:product_version": "V200"
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [-120, 33],
            [-119, 33],
            [-119, 34],
            [-120, 34],
            [-120, 33]
        ]]
    },
    "links": [],
    "assets": {
        "map": {
            "href": "https://ai4edatasetspublicassets.blob.core.windows.net/assets/aod_esa-worldcover/v200/2021/map/ESA_WorldCover_10m_2021_v200_N33W120_Map.tif",
            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            "title": "Land Cover Classes",
            "raster:bands": [{"nodata": 0, "data_type": "uint8", "spatial_resolution": 10}],
            "proj:shape": [36000, 36000],
            "proj:transform": [0.000277777777778, 0, -120, 0, -0.000277777777778, 34]
        }
    },
    "bbox": [-120, 33, -119, 34],
    "stac_extensions": [
        "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
        "https://stac-extensions.github.io/raster/v1.0.0/schema.json"
    ],
    "collection": "esa-worldcover"
}

# OSMnx Mock Graph Data
def create_mock_osmnx_graph():
    """Create a mock NetworkX graph similar to OSMnx output."""
    import networkx as nx
    
    G = nx.MultiDiGraph()
    
    # Add nodes with coordinates
    G.add_node(1, y=34.0522, x=-118.2437, osmid=1)
    G.add_node(2, y=34.0523, x=-118.2438, osmid=2)
    G.add_node(3, y=34.0524, x=-118.2439, osmid=3)
    G.add_node(4, y=34.0525, x=-118.2440, osmid=4)
    
    # Add edges with attributes
    G.add_edge(1, 2, length=100.5, highway='primary', osmid=101)
    G.add_edge(2, 3, length=150.3, highway='secondary', osmid=102)
    G.add_edge(3, 4, length=200.7, highway='primary', osmid=103)
    G.add_edge(1, 3, length=250.2, highway='tertiary', osmid=104)
    
    # Add graph attributes
    G.graph['crs'] = 'EPSG:4326'
    G.graph['name'] = 'Mock Street Network'
    
    return G

# Mock raster data for satellite imagery
def create_mock_raster_data(shape=(100, 100), dtype=np.uint16):
    """Create mock raster data similar to satellite imagery."""
    return np.random.randint(0, 10000, size=shape, dtype=dtype)

def create_mock_ndvi_data(shape=(100, 100)):
    """Create mock NDVI data (float32, -1 to 1)."""
    return np.random.uniform(-0.5, 0.9, size=shape).astype(np.float32)
