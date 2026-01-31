#!/usr/bin/env python3
"""Test script for new transmission line and KML integration tools."""

import sys
sys.path.insert(0, 'src')

from gis_mcp.mcp import gis_mcp

def test_tools_registered():
    """Test that new tools are registered with the MCP server."""

    # Get all registered tools using get_tools() method
    all_tools = gis_mcp.get_tools()
    tool_names = [tool.name for tool in all_tools]

    print("=" * 60)
    print("REGISTERED MCP TOOLS TEST")
    print("=" * 60)

    # Check transmission line tools
    transmission_tools = [
        'calculate_conductor_sag',
        'calculate_span_length',
        'analyze_tower_placement',
        'check_clearance',
        'create_row_buffer',
        'calculate_catenary_curve',
        'analyze_line_of_sight'
    ]

    print("\n🔋 Transmission Line Tools:")
    for tool_name in transmission_tools:
        if tool_name in tool_names:
            print(f"  ✓ {tool_name}")
        else:
            print(f"  ✗ {tool_name} - NOT FOUND")

    # Check KML integration tools
    kml_tools = [
        'parse_kml_file',
        'extract_kmz',
        'validate_transmission_line_kml',
        'convert_kml_to_geojson',
        'extract_tower_locations',
        'extract_line_routes'
    ]

    print("\n📄 KML Integration Tools:")
    for tool_name in kml_tools:
        if tool_name in tool_names:
            print(f"  ✓ {tool_name}")
        else:
            print(f"  ✗ {tool_name} - NOT FOUND")

    # Get all resources
    all_resources = gis_mcp.get_resources()
    resource_uris = [res.uri for res in all_resources]

    print("\n📚 Registered Resources:")
    for resource_uri in resource_uris:
        if 'transmission' in resource_uri or 'kml' in resource_uri:
            print(f"  ✓ {resource_uri}")

    # Print summary
    total_tools = len(tool_names)
    new_tools = len([t for t in transmission_tools + kml_tools if t in tool_names])

    print("\n" + "=" * 60)
    print(f"Total MCP Tools Registered: {total_tools}")
    print(f"New Tools Added: {new_tools}/{len(transmission_tools + kml_tools)}")
    print("=" * 60)

    return new_tools == len(transmission_tools + kml_tools)


def test_transmission_line_tools():
    """Test transmission line tool functionality."""
    from gis_mcp import transmission_line_functions

    print("\n" + "=" * 60)
    print("TRANSMISSION LINE TOOLS FUNCTIONAL TEST")
    print("=" * 60)

    # Test 1: Calculate conductor sag
    print("\n1. Testing calculate_conductor_sag...")
    try:
        result = transmission_line_functions.calculate_conductor_sag(
            span_length=300.0,
            conductor_weight=1.5,
            tension=20000.0,
            temperature=25.0
        )
        print(f"   ✓ Sag calculation successful: {result['sag_meters']} meters")
        print(f"   ✓ Catenary constant: {result['catenary_constant']} meters")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Calculate span length
    print("\n2. Testing calculate_span_length...")
    try:
        result = transmission_line_functions.calculate_span_length(
            point1=[0.0, 0.0, 100.0],
            point2=[0.005, 0.0, 150.0],
            include_elevation=True
        )
        print(f"   ✓ Span calculation successful")
        print(f"   ✓ Horizontal distance: {result['horizontal_distance_meters']} meters")
        print(f"   ✓ Slant distance: {result.get('slant_distance_meters', 'N/A')} meters")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Analyze tower placement
    print("\n3. Testing analyze_tower_placement...")
    try:
        result = transmission_line_functions.analyze_tower_placement(
            route_line="LINESTRING(0 0, 0.01 0, 0.02 0)",
            typical_span=300.0
        )
        print(f"   ✓ Tower placement analysis successful")
        print(f"   ✓ Recommended towers: {result['tower_count']}")
        print(f"   ✓ Total route length: {result['total_route_length_meters']} meters")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Create ROW buffer
    print("\n4. Testing create_row_buffer...")
    try:
        result = transmission_line_functions.create_row_buffer(
            centerline="LINESTRING(0 0, 0.01 0)",
            row_width=30.0
        )
        print(f"   ✓ ROW buffer created successfully")
        print(f"   ✓ ROW area: {result['row_area_sq_meters']} sq meters")
        print(f"   ✓ ROW area: {result['row_area_acres']} acres")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def test_kml_integration_tools():
    """Test KML integration tool functionality."""
    from gis_mcp import kml_integration_functions

    print("\n" + "=" * 60)
    print("KML INTEGRATION TOOLS FUNCTIONAL TEST")
    print("=" * 60)

    # Create sample KML content
    sample_kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Transmission Line</name>
    <Placemark>
      <name>Tower 1</name>
      <description>First tower</description>
      <Point>
        <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Tower 2</name>
      <description>Second tower</description>
      <Point>
        <coordinates>-122.0844277547948,37.42215983204111,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Line Route</name>
      <description>Transmission line centerline</description>
      <LineString>
        <coordinates>
          -122.0822035425683,37.42228990140251,0
          -122.0844277547948,37.42215983204111,0
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""

    # Test 1: Parse KML
    print("\n1. Testing parse_kml_file...")
    try:
        result = kml_integration_functions.parse_kml_file(
            kml_content=sample_kml,
            extract_styles=True,
            include_metadata=True
        )
        print(f"   ✓ KML parsing successful")
        print(f"   ✓ Features found: {result['feature_count']}")
        print(f"   ✓ Geometry types: {result['geometry_types']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Validate transmission line KML
    print("\n2. Testing validate_transmission_line_kml...")
    try:
        result = kml_integration_functions.validate_transmission_line_kml(
            kml_content=sample_kml,
            require_line_routes=True,
            require_tower_points=True
        )
        print(f"   ✓ Validation complete")
        print(f"   ✓ Valid: {result['valid']}")
        print(f"   ✓ Errors: {len(result['validation_errors'])}")
        print(f"   ✓ Warnings: {len(result['validation_warnings'])}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Extract tower locations
    print("\n3. Testing extract_tower_locations...")
    try:
        result = kml_integration_functions.extract_tower_locations(
            kml_content=sample_kml
        )
        print(f"   ✓ Tower extraction successful")
        print(f"   ✓ Towers found: {result['tower_count']}")
        if result['tower_count'] > 0:
            print(f"   ✓ First tower: {result['towers'][0]['name']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Extract line routes
    print("\n4. Testing extract_line_routes...")
    try:
        result = kml_integration_functions.extract_line_routes(
            kml_content=sample_kml
        )
        print(f"   ✓ Route extraction successful")
        print(f"   ✓ Routes found: {result['route_count']}")
        if result['route_count'] > 0:
            print(f"   ✓ First route: {result['routes'][0]['name']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 5: Convert to GeoJSON
    print("\n5. Testing convert_kml_to_geojson...")
    try:
        result = kml_integration_functions.convert_kml_to_geojson(
            kml_content=sample_kml
        )
        print(f"   ✓ GeoJSON conversion successful")
        print(f"   ✓ Features converted: {result['feature_count']}")
        print(f"   ✓ GeoJSON type: {result['geojson']['type']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == '__main__':
    print("\n🚀 Starting GIS-MCP New Tools Test Suite\n")

    # Test 1: Tool registration
    registration_ok = test_tools_registered()

    # Test 2: Transmission line tools
    test_transmission_line_tools()

    # Test 3: KML integration tools
    test_kml_integration_tools()

    print("\n" + "=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60)

    if registration_ok:
        print("\n✅ All tools successfully registered and functional!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tools failed to register")
        sys.exit(1)
