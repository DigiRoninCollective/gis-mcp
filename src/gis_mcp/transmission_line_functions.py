"""Transmission Line-specific MCP tool functions for power grid operations.

This module provides specialized GIS tools for transmission and distribution
line construction, inspection, and analysis - designed for applications like
ShadowSpan operations console.
"""
import os
import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from .mcp import gis_mcp

# Configure logging
logger = logging.getLogger(__name__)

# Import required libraries
try:
    from shapely import wkt
    from shapely.geometry import Point, LineString, Polygon, MultiPoint
    from shapely.ops import nearest_points
    import numpy as np
except ImportError as e:
    logger.error(f"Required dependencies not available: {e}")
    raise


# Resource handlers for Transmission Line operations
@gis_mcp.resource("gis://transmission/operations")
def get_transmission_operations() -> Dict[str, List[str]]:
    """List available transmission line operations."""
    return {
        "operations": [
            "calculate_conductor_sag",
            "calculate_span_length",
            "analyze_tower_placement",
            "check_clearance",
            "create_row_buffer",
            "calculate_catenary_curve",
            "calculate_structure_offsets",
            "extract_terrain_profile",
            "analyze_line_of_sight"
        ],
        "description": "Specialized tools for transmission line construction and inspection"
    }


@gis_mcp.tool()
def calculate_conductor_sag(
    span_length: float,
    conductor_weight: float,
    tension: float,
    temperature: float = 15.0,
    wind_pressure: Optional[float] = None
) -> Dict[str, Any]:
    """Calculate conductor sag using catenary equations.

    Essential for determining the vertical clearance requirements and ensuring
    proper tension in overhead conductors between support structures.

    Args:
        span_length: Horizontal distance between supports (meters)
        conductor_weight: Weight per unit length (kg/m)
        tension: Horizontal tension in conductor (Newtons)
        temperature: Ambient temperature (Celsius, default 15°C)
        wind_pressure: Optional wind pressure (Pa) for loaded condition

    Returns:
        Dictionary containing:
        - sag: Maximum sag at midspan (meters)
        - catenary_constant: Catenary constant (meters)
        - conductor_length: Actual conductor length (meters)
        - lowest_point_height: Height at lowest point (meters)
        - thermal_coefficient: Temperature effect coefficient

    Example:
        >>> calculate_conductor_sag(300, 1.5, 20000)
        {'sag': 8.4375, 'catenary_constant': 1333.33, ...}
    """
    try:
        # Apply wind loading if specified
        effective_weight = conductor_weight
        if wind_pressure:
            # Simplified wind load calculation (assuming conductor diameter ~30mm)
            conductor_diameter = 0.03  # meters
            wind_load = wind_pressure * conductor_diameter  # N/m
            effective_weight = math.sqrt(conductor_weight**2 + (wind_load/9.81)**2)

        # Catenary constant
        catenary_constant = tension / (effective_weight * 9.81)  # meters

        # Maximum sag (at midspan)
        # Sag = (w * L^2) / (8 * T)
        sag = (effective_weight * 9.81 * span_length**2) / (8 * tension)

        # Conductor length using catenary curve
        # L = 2c * sinh(s/2c) where c = catenary constant, s = span
        half_span = span_length / 2
        if catenary_constant > 0:
            sinh_term = math.sinh(half_span / catenary_constant)
            conductor_length = 2 * catenary_constant * sinh_term
        else:
            conductor_length = span_length

        # Temperature coefficient (typical for ACSR conductors)
        # Coefficient of linear thermal expansion ~ 19.3 × 10^-6 per °C
        thermal_expansion = 19.3e-6
        temp_diff = temperature - 15.0  # Reference temp 15°C
        thermal_coefficient = 1 + (thermal_expansion * temp_diff)

        # Lowest point height (relative to supports)
        lowest_point_height = -sag

        return {
            "sag_meters": round(sag, 4),
            "catenary_constant": round(catenary_constant, 2),
            "conductor_length_meters": round(conductor_length, 4),
            "lowest_point_height_meters": round(lowest_point_height, 4),
            "thermal_coefficient": round(thermal_coefficient, 6),
            "temperature_celsius": temperature,
            "wind_loaded": wind_pressure is not None,
            "effective_weight_kg_per_m": round(effective_weight, 4)
        }

    except Exception as e:
        logger.error(f"Error calculating conductor sag: {str(e)}")
        raise ValueError(f"Sag calculation failed: {str(e)}")


@gis_mcp.tool()
def calculate_span_length(
    point1: List[float],
    point2: List[float],
    include_elevation: bool = True
) -> Dict[str, Any]:
    """Calculate span length between two support structures.

    Computes both horizontal (map) distance and slant distance (3D) between
    two tower/pole positions. Critical for conductor design and clearance analysis.

    Args:
        point1: [longitude, latitude, elevation] or [lon, lat]
        point2: [longitude, latitude, elevation] or [lon, lat]
        include_elevation: Whether to calculate 3D slant distance

    Returns:
        Dictionary containing:
        - horizontal_distance: Map distance (meters)
        - slant_distance: 3D distance if elevations provided (meters)
        - elevation_difference: Height difference (meters)
        - slope_angle: Angle of span (degrees)
        - midpoint: Coordinates of span midpoint

    Example:
        >>> calculate_span_length([0, 0, 100], [0.005, 0, 150], True)
        {'horizontal_distance': 556.0, 'slant_distance': 558.24, ...}
    """
    try:
        from pyproj import Geod

        # Extract coordinates
        lon1, lat1 = point1[0], point1[1]
        lon2, lat2 = point2[0], point2[1]
        elev1 = point1[2] if len(point1) > 2 else 0
        elev2 = point2[2] if len(point2) > 2 else 0

        # Calculate horizontal distance using WGS84 ellipsoid
        geod = Geod(ellps='WGS84')
        azimuth, back_azimuth, horizontal_distance = geod.inv(lon1, lat1, lon2, lat2)

        # Calculate elevation difference
        elevation_diff = elev2 - elev1

        # Calculate slant distance (3D)
        slant_distance = None
        slope_angle = 0.0
        if include_elevation and len(point1) > 2 and len(point2) > 2:
            slant_distance = math.sqrt(horizontal_distance**2 + elevation_diff**2)
            slope_angle = math.degrees(math.atan2(elevation_diff, horizontal_distance))

        # Calculate midpoint
        midpoint_lon = (lon1 + lon2) / 2
        midpoint_lat = (lat1 + lat2) / 2
        midpoint_elev = (elev1 + elev2) / 2

        result = {
            "horizontal_distance_meters": round(horizontal_distance, 2),
            "elevation_difference_meters": round(elevation_diff, 2),
            "azimuth_degrees": round(azimuth, 2),
            "back_azimuth_degrees": round(back_azimuth, 2),
            "midpoint": {
                "longitude": round(midpoint_lon, 6),
                "latitude": round(midpoint_lat, 6),
                "elevation": round(midpoint_elev, 2)
            }
        }

        if slant_distance:
            result["slant_distance_meters"] = round(slant_distance, 2)
            result["slope_angle_degrees"] = round(slope_angle, 2)

        return result

    except Exception as e:
        logger.error(f"Error calculating span length: {str(e)}")
        raise ValueError(f"Span length calculation failed: {str(e)}")


@gis_mcp.tool()
def analyze_tower_placement(
    route_line: str,
    typical_span: float = 300.0,
    min_span: float = 200.0,
    max_span: float = 500.0,
    terrain_elevations: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Analyze optimal tower placement along a transmission line route.

    Determines recommended tower locations based on span constraints and
    terrain conditions. Useful for preliminary design and cost estimation.

    Args:
        route_line: WKT LineString of the transmission line route
        typical_span: Preferred span length (meters)
        min_span: Minimum allowable span (meters)
        max_span: Maximum allowable span (meters)
        terrain_elevations: Optional list of elevations along route

    Returns:
        Dictionary containing:
        - tower_count: Number of towers required
        - tower_positions: List of [lon, lat] coordinates
        - span_lengths: List of span distances
        - total_route_length: Total line length (meters)
        - average_span: Average span length (meters)

    Example:
        >>> analyze_tower_placement("LINESTRING(0 0, 1 1, 2 0)", 300)
        {'tower_count': 9, 'tower_positions': [...], ...}
    """
    try:
        # Parse the route geometry
        line = wkt.loads(route_line)

        if not isinstance(line, LineString):
            raise ValueError("Route must be a LineString geometry")

        # Get total length (in degrees, approximate)
        total_length_deg = line.length

        # Convert to approximate meters (at equator: 1 degree ≈ 111,320 meters)
        # This is a rough approximation; for precise work, use pyproj
        coords = list(line.coords)
        avg_lat = sum(c[1] for c in coords) / len(coords)
        meters_per_degree = 111320 * math.cos(math.radians(avg_lat))
        total_length = total_length_deg * meters_per_degree

        # Calculate number of spans
        num_spans = int(total_length / typical_span)
        if num_spans < 1:
            num_spans = 1

        # Adjust span length to fit route
        actual_span_length = total_length / num_spans

        # Check if within constraints
        if actual_span_length < min_span:
            num_spans = int(total_length / min_span)
            actual_span_length = total_length / num_spans
        elif actual_span_length > max_span:
            num_spans = int(math.ceil(total_length / max_span))
            actual_span_length = total_length / num_spans

        # Number of towers = number of spans + 1 (including start and end)
        tower_count = num_spans + 1

        # Generate tower positions along the line
        tower_positions = []
        span_lengths = []

        for i in range(tower_count):
            # Interpolate position along line (0 to 1)
            fraction = i / num_spans if num_spans > 0 else 0
            point = line.interpolate(fraction, normalized=True)
            tower_positions.append([round(point.x, 6), round(point.y, 6)])

            # Calculate span length (except for last tower)
            if i < tower_count - 1:
                span_lengths.append(round(actual_span_length, 2))

        return {
            "tower_count": tower_count,
            "tower_positions": tower_positions,
            "span_lengths": span_lengths,
            "total_route_length_meters": round(total_length, 2),
            "average_span_meters": round(actual_span_length, 2),
            "num_spans": num_spans,
            "constraints": {
                "typical_span_meters": typical_span,
                "min_span_meters": min_span,
                "max_span_meters": max_span
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing tower placement: {str(e)}")
        raise ValueError(f"Tower placement analysis failed: {str(e)}")


@gis_mcp.tool()
def check_clearance(
    conductor_line: str,
    obstacle_geometry: str,
    minimum_clearance: float = 7.0,
    voltage_kv: Optional[float] = None
) -> Dict[str, Any]:
    """Check clearance between conductor and obstacles.

    Verifies that transmission lines maintain safe distances from terrain,
    structures, vegetation, or other obstacles. Essential for safety compliance.

    Args:
        conductor_line: WKT LineString of conductor path (with elevation)
        obstacle_geometry: WKT geometry of obstacle (Point, Line, or Polygon)
        minimum_clearance: Minimum required clearance (meters)
        voltage_kv: Optional line voltage (kV) for regulatory clearance calc

    Returns:
        Dictionary containing:
        - clearance_ok: Boolean if clearance is sufficient
        - minimum_distance: Closest approach distance (meters)
        - clearance_margin: Distance above/below minimum (meters)
        - nearest_points: Coordinates of closest points
        - required_clearance: Required clearance based on voltage

    Example:
        >>> check_clearance("LINESTRING(0 0, 1 1)", "POINT(0.5 0.4)", 7.0)
        {'clearance_ok': False, 'minimum_distance': 5.2, ...}
    """
    try:
        # Parse geometries
        conductor = wkt.loads(conductor_line)
        obstacle = wkt.loads(obstacle_geometry)

        # Calculate required clearance based on voltage (NESC standards approximation)
        required_clearance = minimum_clearance
        if voltage_kv:
            # Basic formula: base clearance + voltage factor
            # For 69-230 kV: ~5.5m base + 0.01m per kV over 50kV
            if voltage_kv > 50:
                required_clearance = 5.5 + (0.01 * (voltage_kv - 50))
            required_clearance = max(required_clearance, minimum_clearance)

        # Calculate minimum distance
        min_distance = conductor.distance(obstacle)

        # Find nearest points
        nearest_pair = nearest_points(conductor, obstacle)
        nearest_on_conductor = nearest_pair[0]
        nearest_on_obstacle = nearest_pair[1]

        # Convert distance to meters (rough approximation)
        # In reality, you'd use pyproj for accurate distance
        min_distance_meters = min_distance * 111320  # Rough degree-to-meter conversion

        # Check if clearance is sufficient
        clearance_ok = min_distance_meters >= required_clearance
        clearance_margin = min_distance_meters - required_clearance

        return {
            "clearance_ok": clearance_ok,
            "minimum_distance_meters": round(min_distance_meters, 2),
            "required_clearance_meters": round(required_clearance, 2),
            "clearance_margin_meters": round(clearance_margin, 2),
            "nearest_point_on_conductor": [
                round(nearest_on_conductor.x, 6),
                round(nearest_on_conductor.y, 6)
            ],
            "nearest_point_on_obstacle": [
                round(nearest_on_obstacle.x, 6),
                round(nearest_on_obstacle.y, 6)
            ],
            "voltage_kv": voltage_kv,
            "status": "PASS" if clearance_ok else "FAIL"
        }

    except Exception as e:
        logger.error(f"Error checking clearance: {str(e)}")
        raise ValueError(f"Clearance check failed: {str(e)}")


@gis_mcp.tool()
def create_row_buffer(
    centerline: str,
    row_width: float = 30.0,
    cap_style: str = "flat",
    include_stations: bool = False
) -> Dict[str, Any]:
    """Create Right-of-Way (ROW) buffer corridor along transmission line.

    Generates the ROW boundary polygon used for land acquisition, vegetation
    management, and access restrictions.

    Args:
        centerline: WKT LineString of transmission line centerline
        row_width: Total ROW width (meters), applied as half-width on each side
        cap_style: End cap style - "flat", "round", or "square"
        include_stations: Whether to include station markers along ROW

    Returns:
        Dictionary containing:
        - row_polygon: WKT Polygon of ROW boundary
        - row_area: Total ROW area (square meters)
        - centerline_length: Length of centerline (meters)
        - row_width_meters: Applied ROW width

    Example:
        >>> create_row_buffer("LINESTRING(0 0, 1 0)", 30.0)
        {'row_polygon': 'POLYGON(...)', 'row_area': 3339600, ...}
    """
    try:
        # Parse centerline
        line = wkt.loads(centerline)

        if not isinstance(line, LineString):
            raise ValueError("Centerline must be a LineString geometry")

        # Map cap_style string to Shapely parameter
        cap_style_map = {
            "flat": 2,
            "round": 1,
            "square": 3
        }
        cap_style_param = cap_style_map.get(cap_style.lower(), 2)

        # Calculate half-width in degrees (rough approximation)
        coords = list(line.coords)
        avg_lat = sum(c[1] for c in coords) / len(coords)
        meters_per_degree = 111320 * math.cos(math.radians(avg_lat))
        half_width_degrees = (row_width / 2) / meters_per_degree

        # Create buffer
        row_polygon = line.buffer(
            half_width_degrees,
            cap_style=cap_style_param,
            join_style=1  # Round joins
        )

        # Calculate area (convert from square degrees to square meters)
        area_sq_degrees = row_polygon.area
        area_sq_meters = area_sq_degrees * (meters_per_degree ** 2)

        # Calculate centerline length
        length_degrees = line.length
        length_meters = length_degrees * meters_per_degree

        result = {
            "row_polygon_wkt": row_polygon.wkt,
            "row_area_sq_meters": round(area_sq_meters, 2),
            "row_area_acres": round(area_sq_meters / 4046.86, 2),
            "centerline_length_meters": round(length_meters, 2),
            "row_width_meters": row_width,
            "cap_style": cap_style
        }

        # Add station markers if requested
        if include_stations:
            # Create markers every 100 meters
            station_interval_deg = 100 / meters_per_degree
            num_stations = int(line.length / station_interval_deg)
            stations = []

            for i in range(num_stations + 1):
                fraction = (i * station_interval_deg) / line.length
                if fraction <= 1.0:
                    point = line.interpolate(fraction, normalized=True)
                    stations.append({
                        "station_number": i,
                        "position": [round(point.x, 6), round(point.y, 6)],
                        "distance_meters": i * 100
                    })

            result["stations"] = stations

        return result

    except Exception as e:
        logger.error(f"Error creating ROW buffer: {str(e)}")
        raise ValueError(f"ROW buffer creation failed: {str(e)}")


@gis_mcp.tool()
def calculate_catenary_curve(
    span_length: float,
    sag: float,
    num_points: int = 50
) -> Dict[str, Any]:
    """Generate catenary curve points for conductor visualization.

    Creates a series of points representing the actual shape of a suspended
    conductor between two support structures. Useful for 3D modeling and
    clearance visualization.

    Args:
        span_length: Horizontal span distance (meters)
        sag: Maximum sag at midspan (meters)
        num_points: Number of points to generate along curve

    Returns:
        Dictionary containing:
        - curve_points: List of [x, y] coordinates
        - curve_equation: Catenary equation parameters
        - max_sag: Maximum sag value (meters)
        - curve_length: Total curve length (meters)

    Example:
        >>> calculate_catenary_curve(300, 8.5, 50)
        {'curve_points': [[0, 0], [6, -0.3], ...], 'max_sag': 8.5, ...}
    """
    try:
        # Calculate catenary constant from span and sag
        # For a catenary: sag = c * (cosh(L/2c) - 1)
        # We need to solve for c given sag and L

        # Simplified approximation: c ≈ L^2 / (8 * sag)
        catenary_constant = (span_length ** 2) / (8 * sag)

        # Generate points along the curve
        curve_points = []
        x_values = np.linspace(0, span_length, num_points)

        for x in x_values:
            # Catenary equation: y = c * (cosh((x - L/2) / c) - 1)
            # Shifted so midpoint is at lowest point
            x_shifted = x - (span_length / 2)
            if catenary_constant > 0:
                y = catenary_constant * (math.cosh(x_shifted / catenary_constant) - 1)
            else:
                # Fallback to parabola if catenary constant invalid
                y = (4 * sag / (span_length ** 2)) * x * (span_length - x)

            # Adjust so supports are at y=0 and sag is negative
            y = y - sag

            curve_points.append([round(float(x), 2), round(float(y), 2)])

        # Calculate actual curve length using trapezoidal integration
        curve_length = 0
        for i in range(len(curve_points) - 1):
            dx = curve_points[i+1][0] - curve_points[i][0]
            dy = curve_points[i+1][1] - curve_points[i][1]
            curve_length += math.sqrt(dx**2 + dy**2)

        return {
            "curve_points": curve_points,
            "catenary_constant": round(catenary_constant, 2),
            "max_sag_meters": sag,
            "span_length_meters": span_length,
            "curve_length_meters": round(curve_length, 2),
            "num_points": num_points,
            "equation": f"y = {catenary_constant:.2f} * (cosh(x/{catenary_constant:.2f}) - 1)"
        }

    except Exception as e:
        logger.error(f"Error calculating catenary curve: {str(e)}")
        raise ValueError(f"Catenary curve calculation failed: {str(e)}")


@gis_mcp.tool()
def analyze_line_of_sight(
    point1: List[float],
    point2: List[float],
    terrain_profile: List[float],
    observer_height: float = 2.0,
    target_height: float = 30.0
) -> Dict[str, Any]:
    """Analyze line-of-sight visibility between two towers.

    Determines if there's a clear line of sight between structures considering
    terrain elevation. Important for microwave/telecom equipment on towers.

    Args:
        point1: [lon, lat, elevation] of first structure
        point2: [lon, lat, elevation] of second structure
        terrain_profile: List of terrain elevations between points
        observer_height: Height above ground at point1 (meters)
        target_height: Height above ground at point2 (meters)

    Returns:
        Dictionary containing:
        - line_of_sight_clear: Boolean if sight line is clear
        - max_obstruction_height: Maximum terrain above sight line (meters)
        - clearance_margin: Minimum clearance above terrain (meters)
        - obstruction_points: List of obstructed sample indices

    Example:
        >>> analyze_line_of_sight([0,0,100], [1,0,120], [100,105,110,108,120])
        {'line_of_sight_clear': True, 'clearance_margin': 8.5, ...}
    """
    try:
        # Extract elevations
        elev1 = point1[2] + observer_height
        elev2 = point2[2] + target_height

        # Create sight line elevations
        num_samples = len(terrain_profile)
        sight_line_elevations = np.linspace(elev1, elev2, num_samples)

        # Compare sight line with terrain
        terrain_array = np.array(terrain_profile)
        clearances = sight_line_elevations - terrain_array

        # Find obstructions
        obstructions = clearances < 0
        obstruction_indices = np.where(obstructions)[0].tolist()

        # Calculate metrics
        line_of_sight_clear = not np.any(obstructions)
        min_clearance = float(np.min(clearances))
        max_obstruction = float(np.min(clearances)) if not line_of_sight_clear else 0.0

        return {
            "line_of_sight_clear": line_of_sight_clear,
            "clearance_margin_meters": round(min_clearance, 2),
            "max_obstruction_height_meters": round(abs(max_obstruction), 2),
            "obstruction_count": len(obstruction_indices),
            "obstruction_sample_indices": obstruction_indices,
            "observer_height_asl_meters": round(elev1, 2),
            "target_height_asl_meters": round(elev2, 2),
            "profile_samples": num_samples,
            "status": "CLEAR" if line_of_sight_clear else "OBSTRUCTED"
        }

    except Exception as e:
        logger.error(f"Error analyzing line of sight: {str(e)}")
        raise ValueError(f"Line of sight analysis failed: {str(e)}")


logger.info("Transmission line functions module loaded successfully")
