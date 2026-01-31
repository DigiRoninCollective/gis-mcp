"""KML/KMZ integration tools for transmission line overlay import.

This module provides tools for parsing, validating, and converting KML/KMZ files
containing transmission line routes, tower locations, and related infrastructure.
Designed for integration with ShadowSpan and similar GIS applications.
"""
import os
import logging
import zipfile
import tempfile
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET
from .mcp import gis_mcp

# Configure logging
logger = logging.getLogger(__name__)

# Import required libraries
try:
    from shapely.geometry import Point, LineString, Polygon, MultiPoint, mapping
    from shapely import wkt
    import json
except ImportError as e:
    logger.error(f"Required dependencies not available: {e}")
    raise


# KML namespace
KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}


@gis_mcp.resource("gis://kml/operations")
def get_kml_operations() -> Dict[str, List[str]]:
    """List available KML/KMZ operations."""
    return {
        "operations": [
            "parse_kml_file",
            "extract_kmz",
            "validate_transmission_line_kml",
            "convert_kml_to_geojson",
            "extract_tower_locations",
            "extract_line_routes"
        ],
        "description": "Tools for KML/KMZ overlay import and validation"
    }


def _parse_kml_file_internal(
    kml_content: str,
    extract_styles: bool = True,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """Internal KML parsing function."""
    """Parse KML content and extract geographic features.

    Processes KML XML to extract placemarks, geometries, and metadata.
    Supports Points, LineStrings, and Polygons.

    Args:
        kml_content: KML file content as string
        extract_styles: Whether to extract style information
        include_metadata: Whether to include extended data and descriptions

    Returns:
        Dictionary containing:
        - features: List of extracted features with geometries
        - feature_count: Total number of features
        - geometry_types: Summary of geometry types found
        - styles: Style definitions if extract_styles=True
        - metadata: Document-level metadata

    Example:
        >>> parse_kml_file(kml_string, True, True)
        {'features': [...], 'feature_count': 45, ...}
    """
    try:
        # Parse XML
        root = ET.fromstring(kml_content)

        features = []
        styles = {}
        metadata = {}

        # Extract document metadata
        if include_metadata:
            doc_name = root.find('.//kml:Document/kml:name', KML_NS)
            doc_desc = root.find('.//kml:Document/kml:description', KML_NS)

            metadata = {
                "name": doc_name.text if doc_name is not None else None,
                "description": doc_desc.text if doc_desc is not None else None
            }

        # Extract styles if requested
        if extract_styles:
            for style_elem in root.findall('.//kml:Style', KML_NS):
                style_id = style_elem.get('id')
                if style_id:
                    styles[style_id] = _extract_style_info(style_elem)

        # Extract placemarks
        for placemark in root.findall('.//kml:Placemark', KML_NS):
            feature = _parse_placemark(placemark, include_metadata)
            if feature:
                features.append(feature)

        # Analyze geometry types
        geometry_types = {}
        for feature in features:
            geom_type = feature.get('geometry_type')
            geometry_types[geom_type] = geometry_types.get(geom_type, 0) + 1

        result = {
            "features": features,
            "feature_count": len(features),
            "geometry_types": geometry_types,
            "success": True
        }

        if extract_styles:
            result["styles"] = styles

        if include_metadata:
            result["metadata"] = metadata

        return result

    except ET.ParseError as e:
        logger.error(f"KML parse error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid KML format: {str(e)}",
            "features": [],
            "feature_count": 0
        }
    except Exception as e:
        logger.error(f"Error parsing KML: {str(e)}")
        raise ValueError(f"KML parsing failed: {str(e)}")


@gis_mcp.tool()
def parse_kml_file(
    kml_content: str,
    extract_styles: bool = True,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """Parse KML content and extract geographic features.

    Processes KML XML to extract placemarks, geometries, and metadata.
    Supports Points, LineStrings, and Polygons.

    Args:
        kml_content: KML file content as string
        extract_styles: Whether to extract style information
        include_metadata: Whether to include extended data and descriptions

    Returns:
        Dictionary containing:
        - features: List of extracted features with geometries
        - feature_count: Total number of features
        - geometry_types: Summary of geometry types found
        - styles: Style definitions if extract_styles=True
        - metadata: Document-level metadata

    Example:
        >>> parse_kml_file(kml_string, True, True)
        {'features': [...], 'feature_count': 45, ...}
    """
    return _parse_kml_file_internal(kml_content, extract_styles, include_metadata)


def _parse_placemark(placemark: ET.Element, include_metadata: bool) -> Optional[Dict[str, Any]]:
    """Parse a KML Placemark element."""
    try:
        # Extract name and description
        name_elem = placemark.find('kml:name', KML_NS)
        desc_elem = placemark.find('kml:description', KML_NS)

        name = name_elem.text if name_elem is not None else None
        description = desc_elem.text if desc_elem is not None else None

        # Extract geometry
        point = placemark.find('.//kml:Point/kml:coordinates', KML_NS)
        linestring = placemark.find('.//kml:LineString/kml:coordinates', KML_NS)
        polygon = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)

        geometry = None
        geometry_type = None
        coordinates = None

        if point is not None:
            geometry_type = "Point"
            coords = _parse_coordinates(point.text)
            if coords:
                coordinates = coords[0]
                geometry = Point(coordinates[:2])  # lon, lat

        elif linestring is not None:
            geometry_type = "LineString"
            coords = _parse_coordinates(linestring.text)
            if coords:
                coordinates = coords
                geometry = LineString([(c[0], c[1]) for c in coords])

        elif polygon is not None:
            geometry_type = "Polygon"
            coords = _parse_coordinates(polygon.text)
            if coords:
                coordinates = coords
                geometry = Polygon([(c[0], c[1]) for c in coords])

        if geometry is None:
            return None

        feature = {
            "name": name,
            "description": description,
            "geometry_type": geometry_type,
            "geometry_wkt": geometry.wkt,
            "coordinates": coordinates
        }

        # Extract extended data if requested
        if include_metadata:
            extended_data = {}
            for data_elem in placemark.findall('.//kml:ExtendedData/kml:Data', KML_NS):
                data_name = data_elem.get('name')
                value_elem = data_elem.find('kml:value', KML_NS)
                if data_name and value_elem is not None:
                    extended_data[data_name] = value_elem.text

            if extended_data:
                feature["extended_data"] = extended_data

        return feature

    except Exception as e:
        logger.warning(f"Error parsing placemark: {str(e)}")
        return None


def _parse_coordinates(coord_text: str) -> List[List[float]]:
    """Parse KML coordinate string."""
    coords = []
    if coord_text:
        for coord_str in coord_text.strip().split():
            parts = coord_str.split(',')
            if len(parts) >= 2:
                lon = float(parts[0])
                lat = float(parts[1])
                elev = float(parts[2]) if len(parts) > 2 else 0.0
                coords.append([lon, lat, elev])
    return coords


def _extract_style_info(style_elem: ET.Element) -> Dict[str, Any]:
    """Extract style information from Style element."""
    style_info = {}

    # Line style
    line_style = style_elem.find('kml:LineStyle', KML_NS)
    if line_style is not None:
        color = line_style.find('kml:color', KML_NS)
        width = line_style.find('kml:width', KML_NS)
        style_info['line'] = {
            'color': color.text if color is not None else None,
            'width': float(width.text) if width is not None else 1.0
        }

    # Icon style
    icon_style = style_elem.find('kml:IconStyle', KML_NS)
    if icon_style is not None:
        icon = icon_style.find('kml:Icon/kml:href', KML_NS)
        scale = icon_style.find('kml:scale', KML_NS)
        style_info['icon'] = {
            'href': icon.text if icon is not None else None,
            'scale': float(scale.text) if scale is not None else 1.0
        }

    return style_info


@gis_mcp.tool()
def extract_kmz(
    kmz_path: str,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Extract KMZ archive and return main KML content.

    KMZ files are ZIP archives containing KML and supporting files.
    This tool extracts the archive and identifies the main KML file.

    Args:
        kmz_path: Path to KMZ file
        output_dir: Optional directory for extraction (uses temp dir if not specified)

    Returns:
        Dictionary containing:
        - kml_content: Main KML file content as string
        - kml_filename: Name of main KML file
        - extracted_files: List of all extracted files
        - extraction_path: Path to extracted directory

    Example:
        >>> extract_kmz("/path/to/transmission_line.kmz")
        {'kml_content': '<?xml version...', 'extracted_files': [...], ...}
    """
    try:
        # Use temp directory if output_dir not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="kmz_extract_")

        # Extract KMZ (which is a ZIP file)
        with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
            extracted_files = zip_ref.namelist()

        # Find main KML file (usually doc.kml or the first .kml file)
        kml_files = [f for f in extracted_files if f.lower().endswith('.kml')]

        if not kml_files:
            raise ValueError("No KML file found in KMZ archive")

        # Prefer doc.kml, otherwise use first KML file
        main_kml = 'doc.kml' if 'doc.kml' in kml_files else kml_files[0]
        kml_path = os.path.join(output_dir, main_kml)

        # Read KML content
        with open(kml_path, 'r', encoding='utf-8') as f:
            kml_content = f.read()

        return {
            "success": True,
            "kml_content": kml_content,
            "kml_filename": main_kml,
            "extracted_files": extracted_files,
            "extraction_path": output_dir,
            "kml_file_count": len(kml_files)
        }

    except zipfile.BadZipFile:
        logger.error(f"Invalid KMZ file: {kmz_path}")
        return {
            "success": False,
            "error": "Invalid KMZ file (not a valid ZIP archive)"
        }
    except Exception as e:
        logger.error(f"Error extracting KMZ: {str(e)}")
        raise ValueError(f"KMZ extraction failed: {str(e)}")


@gis_mcp.tool()
def validate_transmission_line_kml(
    kml_content: str,
    require_line_routes: bool = True,
    require_tower_points: bool = True
) -> Dict[str, Any]:
    """Validate KML for transmission line data integrity.

    Checks if KML contains required elements for transmission line operations
    such as line routes (LineStrings) and tower locations (Points).

    Args:
        kml_content: KML file content as string
        require_line_routes: Whether LineString geometries are required
        require_tower_points: Whether Point geometries are required

    Returns:
        Dictionary containing:
        - valid: Boolean indicating if validation passed
        - validation_errors: List of validation error messages
        - validation_warnings: List of non-critical warnings
        - feature_summary: Summary of found features

    Example:
        >>> validate_transmission_line_kml(kml_string, True, True)
        {'valid': True, 'validation_errors': [], ...}
    """
    try:
        # Parse KML
        parse_result = _parse_kml_file_internal(kml_content, False, True)

        if not parse_result.get('success'):
            return {
                "valid": False,
                "validation_errors": ["Failed to parse KML"],
                "validation_warnings": []
            }

        features = parse_result['features']
        geometry_types = parse_result['geometry_types']

        errors = []
        warnings = []

        # Check for required geometry types
        if require_line_routes and geometry_types.get('LineString', 0) == 0:
            errors.append("No LineString features found (required for transmission line routes)")

        if require_tower_points and geometry_types.get('Point', 0) == 0:
            errors.append("No Point features found (required for tower locations)")

        # Check for coordinate validity
        for feature in features:
            coords = feature.get('coordinates', [])
            if not coords:
                warnings.append(f"Feature '{feature.get('name')}' has no coordinates")
                continue

            # Validate coordinate ranges
            if isinstance(coords, list) and isinstance(coords[0], list):
                # Multiple coordinates
                for coord in coords:
                    if not _validate_coordinate(coord):
                        errors.append(f"Invalid coordinate in feature '{feature.get('name')}': {coord}")
            else:
                # Single coordinate
                if not _validate_coordinate(coords):
                    errors.append(f"Invalid coordinate in feature '{feature.get('name')}': {coords}")

        # Check for elevation data
        has_elevation = any(
            len(coord) > 2 and coord[2] != 0
            for feature in features
            for coord in (feature.get('coordinates', []) if isinstance(feature.get('coordinates', [])[0] if feature.get('coordinates') else [], list) else [feature.get('coordinates', [])])
        )

        if not has_elevation:
            warnings.append("No elevation data found in coordinates (z-values are 0 or missing)")

        validation_passed = len(errors) == 0

        return {
            "valid": validation_passed,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "feature_summary": {
                "total_features": parse_result['feature_count'],
                "geometry_types": geometry_types,
                "has_elevation_data": has_elevation
            },
            "metadata": parse_result.get('metadata', {})
        }

    except Exception as e:
        logger.error(f"Error validating KML: {str(e)}")
        return {
            "valid": False,
            "validation_errors": [f"Validation failed: {str(e)}"],
            "validation_warnings": []
        }


def _validate_coordinate(coord: List[float]) -> bool:
    """Validate coordinate values."""
    if len(coord) < 2:
        return False

    lon, lat = coord[0], coord[1]

    # Check valid ranges
    if lon < -180 or lon > 180:
        return False
    if lat < -90 or lat > 90:
        return False

    return True


@gis_mcp.tool()
def convert_kml_to_geojson(
    kml_content: str,
    include_styles: bool = False
) -> Dict[str, Any]:
    """Convert KML features to GeoJSON format.

    Transforms KML placemarks into GeoJSON FeatureCollection for use
    in web mapping applications and GIS software.

    Args:
        kml_content: KML file content as string
        include_styles: Whether to include style info in properties

    Returns:
        Dictionary containing:
        - geojson: GeoJSON FeatureCollection object
        - feature_count: Number of features converted
        - conversion_success: Boolean success indicator

    Example:
        >>> convert_kml_to_geojson(kml_string)
        {'geojson': {'type': 'FeatureCollection', ...}, ...}
    """
    try:
        # Parse KML
        parse_result = _parse_kml_file_internal(kml_content, include_styles, True)

        if not parse_result.get('success'):
            return {
                "conversion_success": False,
                "error": "Failed to parse KML"
            }

        features = parse_result['features']

        # Convert to GeoJSON features
        geojson_features = []

        for feature in features:
            # Create GeoJSON geometry
            geom = wkt.loads(feature['geometry_wkt'])
            geojson_geom = mapping(geom)

            # Create properties
            properties = {
                "name": feature.get('name'),
                "description": feature.get('description')
            }

            # Add extended data
            if 'extended_data' in feature:
                properties.update(feature['extended_data'])

            # Create GeoJSON feature
            geojson_feature = {
                "type": "Feature",
                "geometry": geojson_geom,
                "properties": properties
            }

            geojson_features.append(geojson_feature)

        # Create FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }

        return {
            "conversion_success": True,
            "geojson": geojson,
            "feature_count": len(geojson_features),
            "geojson_string": json.dumps(geojson, indent=2)
        }

    except Exception as e:
        logger.error(f"Error converting KML to GeoJSON: {str(e)}")
        raise ValueError(f"KML to GeoJSON conversion failed: {str(e)}")


@gis_mcp.tool()
def extract_tower_locations(
    kml_content: str,
    name_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Extract tower/structure locations from KML.

    Filters Point features from KML that represent transmission towers,
    poles, or other support structures.

    Args:
        kml_content: KML file content as string
        name_pattern: Optional regex pattern to filter by name (e.g., "Tower.*")

    Returns:
        Dictionary containing:
        - towers: List of tower features with coordinates
        - tower_count: Total number of towers found
        - bounding_box: Geographic extent of all towers

    Example:
        >>> extract_tower_locations(kml_string, "Tower.*")
        {'towers': [...], 'tower_count': 23, ...}
    """
    try:
        import re

        # Parse KML
        parse_result = _parse_kml_file_internal(kml_content, False, True)

        if not parse_result.get('success'):
            return {
                "success": False,
                "error": "Failed to parse KML",
                "towers": [],
                "tower_count": 0
            }

        features = parse_result['features']

        # Filter Point features
        towers = []
        for feature in features:
            if feature['geometry_type'] != 'Point':
                continue

            # Apply name filter if specified
            if name_pattern:
                name = feature.get('name', '')
                if not re.match(name_pattern, name):
                    continue

            towers.append({
                "name": feature.get('name'),
                "coordinates": feature['coordinates'],
                "longitude": feature['coordinates'][0],
                "latitude": feature['coordinates'][1],
                "elevation": feature['coordinates'][2] if len(feature['coordinates']) > 2 else None,
                "description": feature.get('description'),
                "extended_data": feature.get('extended_data', {})
            })

        # Calculate bounding box
        bounding_box = None
        if towers:
            lons = [t['longitude'] for t in towers]
            lats = [t['latitude'] for t in towers]
            bounding_box = {
                "min_lon": min(lons),
                "max_lon": max(lons),
                "min_lat": min(lats),
                "max_lat": max(lats)
            }

        return {
            "success": True,
            "towers": towers,
            "tower_count": len(towers),
            "bounding_box": bounding_box,
            "name_filter_applied": name_pattern is not None
        }

    except Exception as e:
        logger.error(f"Error extracting tower locations: {str(e)}")
        raise ValueError(f"Tower extraction failed: {str(e)}")


@gis_mcp.tool()
def extract_line_routes(
    kml_content: str,
    name_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Extract transmission line routes from KML.

    Filters LineString features from KML that represent transmission
    line centerlines or conductor paths.

    Args:
        kml_content: KML file content as string
        name_pattern: Optional regex pattern to filter by name

    Returns:
        Dictionary containing:
        - routes: List of route features with coordinates
        - route_count: Total number of routes found
        - total_length_estimate: Estimated total route length (degrees)

    Example:
        >>> extract_line_routes(kml_string)
        {'routes': [...], 'route_count': 3, ...}
    """
    try:
        import re

        # Parse KML
        parse_result = _parse_kml_file_internal(kml_content, False, True)

        if not parse_result.get('success'):
            return {
                "success": False,
                "error": "Failed to parse KML",
                "routes": [],
                "route_count": 0
            }

        features = parse_result['features']

        # Filter LineString features
        routes = []
        total_length = 0.0

        for feature in features:
            if feature['geometry_type'] != 'LineString':
                continue

            # Apply name filter if specified
            if name_pattern:
                name = feature.get('name', '')
                if not re.match(name_pattern, name):
                    continue

            # Calculate route length
            geom = wkt.loads(feature['geometry_wkt'])
            route_length = geom.length  # in degrees
            total_length += route_length

            routes.append({
                "name": feature.get('name'),
                "coordinates": feature['coordinates'],
                "geometry_wkt": feature['geometry_wkt'],
                "length_degrees": round(route_length, 6),
                "vertex_count": len(feature['coordinates']),
                "description": feature.get('description'),
                "extended_data": feature.get('extended_data', {})
            })

        return {
            "success": True,
            "routes": routes,
            "route_count": len(routes),
            "total_length_degrees": round(total_length, 6),
            "name_filter_applied": name_pattern is not None
        }

    except Exception as e:
        logger.error(f"Error extracting line routes: {str(e)}")
        raise ValueError(f"Route extraction failed: {str(e)}")


logger.info("KML integration functions module loaded successfully")
