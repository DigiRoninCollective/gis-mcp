#!/usr/bin/env python3
"""Simplified test script for new transmission line and KML integration tools."""

import sys
sys.path.insert(0, 'src')


def test_transmission_line_tools():
    """Test transmission line tool functionality."""
    from gis_mcp import transmission_line_functions

    print("=" * 60)
    print("TRANSMISSION LINE TOOLS FUNCTIONAL TEST")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test 1: Calculate conductor sag
    print("\n1. Testing calculate_conductor_sag...")
    try:
        result = transmission_line_functions.calculate_conductor_sag.fn(
            span_length=300.0,
            conductor_weight=1.5,
            tension=20000.0,
            temperature=25.0
        )
        print(f"   ✓ Sag calculation successful: {result['sag_meters']} meters")
        print(f"   ✓ Catenary constant: {result['catenary_constant']} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 2: Calculate span length
    print("\n2. Testing calculate_span_length...")
    try:
        result = transmission_line_functions.calculate_span_length.fn(
            point1=[0.0, 0.0, 100.0],
            point2=[0.005, 0.0, 150.0],
            include_elevation=True
        )
        print(f"   ✓ Span calculation successful")
        print(f"   ✓ Horizontal distance: {result['horizontal_distance_meters']} meters")
        print(f"   ✓ Slant distance: {result.get('slant_distance_meters', 'N/A')} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 3: Analyze tower placement
    print("\n3. Testing analyze_tower_placement...")
    try:
        result = transmission_line_functions.analyze_tower_placement.fn(
            route_line="LINESTRING(0 0, 0.01 0, 0.02 0)",
            typical_span=300.0
        )
        print(f"   ✓ Tower placement analysis successful")
        print(f"   ✓ Recommended towers: {result['tower_count']}")
        print(f"   ✓ Total route length: {result['total_route_length_meters']} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 4: Create ROW buffer
    print("\n4. Testing create_row_buffer...")
    try:
        result = transmission_line_functions.create_row_buffer.fn(
            centerline="LINESTRING(0 0, 0.01 0)",
            row_width=30.0
        )
        print(f"   ✓ ROW buffer created successfully")
        print(f"   ✓ ROW area: {result['row_area_sq_meters']:.2f} sq meters")
        print(f"   ✓ ROW area: {result['row_area_acres']:.2f} acres")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 5: Calculate catenary curve
    print("\n5. Testing calculate_catenary_curve...")
    try:
        result = transmission_line_functions.calculate_catenary_curve.fn(
            span_length=300.0,
            sag=8.5,
            num_points=50
        )
        print(f"   ✓ Catenary curve generated successfully")
        print(f"   ✓ Number of points: {len(result['curve_points'])}")
        print(f"   ✓ Curve length: {result['curve_length_meters']} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 6: Check clearance
    print("\n6. Testing check_clearance...")
    try:
        result = transmission_line_functions.check_clearance.fn(
            conductor_line="LINESTRING(0 0, 1 1)",
            obstacle_geometry="POINT(0.5 0.4)",
            minimum_clearance=7.0,
            voltage_kv=230.0
        )
        print(f"   ✓ Clearance check successful")
        print(f"   ✓ Clearance status: {result['status']}")
        print(f"   ✓ Minimum distance: {result['minimum_distance_meters']} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 7: Analyze line of sight
    print("\n7. Testing analyze_line_of_sight...")
    try:
        result = transmission_line_functions.analyze_line_of_sight.fn(
            point1=[0, 0, 100],
            point2=[1, 0, 120],
            terrain_profile=[100, 105, 110, 108, 120],
            observer_height=2.0,
            target_height=30.0
        )
        print(f"   ✓ Line of sight analysis successful")
        print(f"   ✓ Line of sight clear: {result['line_of_sight_clear']}")
        print(f"   ✓ Clearance margin: {result['clearance_margin_meters']} meters")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    return passed, failed


def test_kml_integration_tools():
    """Test KML integration tool functionality."""
    from gis_mcp import kml_integration_functions

    print("\n" + "=" * 60)
    print("KML INTEGRATION TOOLS FUNCTIONAL TEST")
    print("=" * 60)

    passed = 0
    failed = 0

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
        result = kml_integration_functions.parse_kml_file.fn(
            kml_content=sample_kml,
            extract_styles=True,
            include_metadata=True
        )
        print(f"   ✓ KML parsing successful")
        print(f"   ✓ Features found: {result['feature_count']}")
        print(f"   ✓ Geometry types: {result['geometry_types']}")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 2: Validate transmission line KML
    print("\n2. Testing validate_transmission_line_kml...")
    try:
        result = kml_integration_functions.validate_transmission_line_kml.fn(
            kml_content=sample_kml,
            require_line_routes=True,
            require_tower_points=True
        )
        print(f"   ✓ Validation complete")
        print(f"   ✓ Valid: {result['valid']}")
        print(f"   ✓ Errors: {len(result['validation_errors'])}")
        print(f"   ✓ Warnings: {len(result['validation_warnings'])}")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 3: Extract tower locations
    print("\n3. Testing extract_tower_locations...")
    try:
        result = kml_integration_functions.extract_tower_locations.fn(
            kml_content=sample_kml
        )
        print(f"   ✓ Tower extraction successful")
        print(f"   ✓ Towers found: {result['tower_count']}")
        if result['tower_count'] > 0:
            print(f"   ✓ First tower: {result['towers'][0]['name']}")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 4: Extract line routes
    print("\n4. Testing extract_line_routes...")
    try:
        result = kml_integration_functions.extract_line_routes.fn(
            kml_content=sample_kml
        )
        print(f"   ✓ Route extraction successful")
        print(f"   ✓ Routes found: {result['route_count']}")
        if result['route_count'] > 0:
            print(f"   ✓ First route: {result['routes'][0]['name']}")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    # Test 5: Convert to GeoJSON
    print("\n5. Testing convert_kml_to_geojson...")
    try:
        result = kml_integration_functions.convert_kml_to_geojson.fn(
            kml_content=sample_kml
        )
        print(f"   ✓ GeoJSON conversion successful")
        print(f"   ✓ Features converted: {result['feature_count']}")
        print(f"   ✓ GeoJSON type: {result['geojson']['type']}")
        passed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        failed += 1

    return passed, failed


if __name__ == '__main__':
    print("\n🚀 Starting GIS-MCP New Tools Test Suite\n")

    total_passed = 0
    total_failed = 0

    # Test transmission line tools
    passed, failed = test_transmission_line_tools()
    total_passed += passed
    total_failed += failed

    # Test KML integration tools
    passed, failed = test_kml_integration_tools()
    total_passed += passed
    total_failed += failed

    print("\n" + "=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60)
    print(f"\n✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Success Rate: {total_passed}/{total_passed + total_failed} ({100*total_passed/(total_passed + total_failed):.1f}%)")

    if total_failed == 0:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_failed} test(s) failed")
        sys.exit(1)
