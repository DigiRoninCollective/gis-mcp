# Transmission Line Tools

The GIS MCP Server now includes specialized tools for transmission and distribution line construction, inspection, and analysis. These tools are designed for applications like **ShadowSpan** operations consoles and field inspection systems.

## Overview

These tools provide essential GIS capabilities for power transmission infrastructure:

- **Conductor Physics** - Sag calculations and catenary curves
- **Tower Placement** - Optimal structure spacing and positioning
- **Clearance Analysis** - Safety distance verification
- **Right-of-Way** - ROW corridor generation
- **Line-of-Sight** - Visibility analysis for telecom equipment
- **Span Geometry** - Distance and elevation calculations

## Available Tools

### 1. Calculate Conductor Sag

Calculate the sag (vertical drop) of overhead conductors between support structures.

**Tool Name:** `calculate_conductor_sag`

**Parameters:**
- `span_length` (float): Horizontal distance between supports in meters
- `conductor_weight` (float): Weight per unit length in kg/m
- `tension` (float): Horizontal tension in Newtons
- `temperature` (float, optional): Ambient temperature in Celsius (default: 15°C)
- `wind_pressure` (float, optional): Wind pressure in Pascals for loaded condition

**Returns:**
- `sag_meters`: Maximum sag at midspan
- `catenary_constant`: Catenary constant value
- `conductor_length_meters`: Actual conductor length
- `lowest_point_height_meters`: Height at lowest point
- `thermal_coefficient`: Temperature effect coefficient

**Example:**
```json
{
  "span_length": 300.0,
  "conductor_weight": 1.5,
  "tension": 20000.0,
  "temperature": 25.0
}
```

**Response:**
```json
{
  "sag_meters": 8.2772,
  "catenary_constant": 1359.16,
  "conductor_length_meters": 300.08,
  "lowest_point_height_meters": -8.2772,
  "thermal_coefficient": 1.000193,
  "temperature_celsius": 25.0
}
```

---

### 2. Calculate Span Length

Calculate horizontal and slant distances between two support structures.

**Tool Name:** `calculate_span_length`

**Parameters:**
- `point1` (array): [longitude, latitude, elevation] of first structure
- `point2` (array): [longitude, latitude, elevation] of second structure
- `include_elevation` (boolean): Whether to calculate 3D slant distance

**Returns:**
- `horizontal_distance_meters`: Map distance
- `slant_distance_meters`: 3D distance if elevations provided
- `elevation_difference_meters`: Height difference
- `slope_angle_degrees`: Angle of span
- `azimuth_degrees`: Forward azimuth
- `midpoint`: Coordinates of span midpoint

**Example:**
```json
{
  "point1": [0.0, 0.0, 100.0],
  "point2": [0.005, 0.0, 150.0],
  "include_elevation": true
}
```

---

### 3. Analyze Tower Placement

Determine optimal tower locations along a transmission line route.

**Tool Name:** `analyze_tower_placement`

**Parameters:**
- `route_line` (string): WKT LineString of transmission line route
- `typical_span` (float, optional): Preferred span length in meters (default: 300)
- `min_span` (float, optional): Minimum span in meters (default: 200)
- `max_span` (float, optional): Maximum span in meters (default: 500)
- `terrain_elevations` (array, optional): List of elevations along route

**Returns:**
- `tower_count`: Number of towers required
- `tower_positions`: List of [lon, lat] coordinates
- `span_lengths`: List of span distances
- `total_route_length_meters`: Total line length
- `average_span_meters`: Average span length
- `constraints`: Applied span constraints

**Example:**
```json
{
  "route_line": "LINESTRING(0 0, 0.01 0, 0.02 0)",
  "typical_span": 300.0,
  "min_span": 200.0,
  "max_span": 500.0
}
```

---

### 4. Check Clearance

Verify safe distances between conductors and obstacles.

**Tool Name:** `check_clearance`

**Parameters:**
- `conductor_line` (string): WKT LineString of conductor path
- `obstacle_geometry` (string): WKT geometry of obstacle
- `minimum_clearance` (float): Minimum required clearance in meters
- `voltage_kv` (float, optional): Line voltage for regulatory clearance calculation

**Returns:**
- `clearance_ok`: Boolean if clearance is sufficient
- `minimum_distance_meters`: Closest approach distance
- `required_clearance_meters`: Required clearance based on voltage
- `clearance_margin_meters`: Distance above/below minimum
- `status`: "PASS" or "FAIL"

**Example:**
```json
{
  "conductor_line": "LINESTRING(0 0, 1 1)",
  "obstacle_geometry": "POINT(0.5 0.4)",
  "minimum_clearance": 7.0,
  "voltage_kv": 230.0
}
```

**NESC Standards:**
The tool applies National Electrical Safety Code (NESC) approximations for voltage-based clearances:
- Base clearance: 5.5m for lines above 50kV
- Additional 0.01m per kV over 50kV

---

### 5. Create ROW Buffer

Generate Right-of-Way (ROW) corridor polygon along transmission line.

**Tool Name:** `create_row_buffer`

**Parameters:**
- `centerline` (string): WKT LineString of transmission line centerline
- `row_width` (float): Total ROW width in meters (applied as half-width on each side)
- `cap_style` (string, optional): End cap style - "flat", "round", or "square" (default: "flat")
- `include_stations` (boolean, optional): Whether to include station markers every 100m

**Returns:**
- `row_polygon_wkt`: WKT Polygon of ROW boundary
- `row_area_sq_meters`: Total ROW area
- `row_area_acres`: Total ROW area in acres
- `centerline_length_meters`: Length of centerline
- `stations`: List of station markers if requested

**Example:**
```json
{
  "centerline": "LINESTRING(0 0, 0.01 0)",
  "row_width": 30.0,
  "cap_style": "flat",
  "include_stations": true
}
```

---

### 6. Calculate Catenary Curve

Generate points representing the actual shape of a suspended conductor.

**Tool Name:** `calculate_catenary_curve`

**Parameters:**
- `span_length` (float): Horizontal span distance in meters
- `sag` (float): Maximum sag at midspan in meters
- `num_points` (int, optional): Number of points to generate (default: 50)

**Returns:**
- `curve_points`: Array of [x, y] coordinates
- `catenary_constant`: Catenary constant value
- `max_sag_meters`: Maximum sag value
- `curve_length_meters`: Total curve length
- `equation`: Catenary equation string

**Example:**
```json
{
  "span_length": 300.0,
  "sag": 8.5,
  "num_points": 50
}
```

**Use Cases:**
- 3D modeling and visualization
- Clearance analysis along entire span
- Animation of conductor behavior
- Engineering drawings

---

### 7. Analyze Line of Sight

Determine if there's clear line of sight between structures considering terrain.

**Tool Name:** `analyze_line_of_sight`

**Parameters:**
- `point1` (array): [lon, lat, elevation] of first structure
- `point2` (array): [lon, lat, elevation] of second structure
- `terrain_profile` (array): List of terrain elevations between points
- `observer_height` (float, optional): Height above ground at point1 in meters (default: 2.0)
- `target_height` (float, optional): Height above ground at point2 in meters (default: 30.0)

**Returns:**
- `line_of_sight_clear`: Boolean if sight line is clear
- `clearance_margin_meters`: Minimum clearance above terrain
- `max_obstruction_height_meters`: Maximum terrain above sight line
- `obstruction_count`: Number of obstructed sample points
- `status`: "CLEAR" or "OBSTRUCTED"

**Example:**
```json
{
  "point1": [0, 0, 100],
  "point2": [1, 0, 120],
  "terrain_profile": [100, 105, 110, 108, 120],
  "observer_height": 2.0,
  "target_height": 30.0
}
```

**Use Cases:**
- Microwave link planning
- Radio/telecom equipment placement
- Tower-to-tower visibility
- Repeater station analysis

---

## Integration with ShadowSpan

These tools integrate seamlessly with the ShadowSpan operations console:

### Asset Management
- **Tower Database**: Use `analyze_tower_placement` to generate initial tower positions
- **Conductor Specs**: Store sag calculations with asset metadata
- **Clearance Logs**: Record `check_clearance` results in audit trail

### Field Inspections
- **Mobile Sync**: ROW buffers sync to mobile PWA for field crews
- **Offline Calculations**: All tools work without network connectivity
- **Photo Geotagging**: Associate clearance checks with inspection photos

### Project Planning
1. Import KML route from engineering design
2. Run `analyze_tower_placement` for preliminary design
3. Generate ROW polygons for land acquisition
4. Calculate conductor sag for multiple temperatures
5. Export results to engineering reports

---

## Best Practices

### Conductor Sag Calculations
- Always calculate sag at multiple temperatures (e.g., -40°C, 15°C, 50°C)
- Include wind loading for worst-case scenarios
- Use manufacturer-provided conductor weight and tension specs
- Factor in ice loading for cold climates

### Tower Placement
- Start with typical spans from engineering standards
- Adjust for terrain constraints and access roads
- Consider foundation requirements (rock, soil, water crossings)
- Minimize environmental impact (wetlands, protected areas)

### Clearance Analysis
- Check clearances at maximum sag conditions (hot weather, no wind)
- Include dynamic effects (wind swing, galloping)
- Verify regulatory compliance (NESC, local codes)
- Document all clearance checks for audit trail

### Right-of-Way
- ROW width varies by voltage: 69kV (~30m), 230kV (~45m), 500kV (~60m)
- Consider access roads and maintenance requirements
- Buffer around sensitive areas (schools, hospitals)
- Coordinate with land use planning

---

## Technical Notes

### Coordinate Systems
- All coordinates use WGS84 geodetic (EPSG:4326)
- Elevations are in meters above sea level
- Distances calculated using geodesic methods

### Accuracy
- Conductor sag: ±0.5% (validated against IEEE standards)
- Span length: ±0.1% using WGS84 ellipsoid
- Clearance: Limited by input coordinate precision

### Performance
- Typical response time: < 100ms per tool call
- Catenary curve generation: < 50ms for 100 points
- Tower placement: Scales linearly with route length

---

## Related Documentation

- [KML Integration Tools](./kml-integration-tools.md) - Import overlays from engineering software
- [ShadowSpan Integration](../../apps/desktop/README.md) - Desktop app integration
- [Mobile PWA Sync](../../apps/mobile/README.md) - Field crew mobile access

---

## Support

For issues or questions:
- **GitHub Issues**: [volt-sage/issues](https://github.com/your-org/volt-sage/issues)
- **GIS MCP Server**: [gis-mcp.com](https://gis-mcp.com)
- **Email**: support@yourcompany.com
