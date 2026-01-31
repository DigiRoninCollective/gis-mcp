"""Tests for administrative boundaries data module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import geopandas as gpd

from gis_mcp.data.administrative_boundaries import download_boundaries
from tests.fixtures.mock_data import MOCK_GADM_GEODATAFRAME


class TestDownloadBoundaries:
    """Test suite for download_boundaries function."""
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_success(self, mock_pygadm, temp_dir):
        """Test successful boundary download."""
        # Setup mock
        mock_adm_items = MagicMock()
        mock_adm_items.to_file = MagicMock()
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        # Execute
        result = download_boundaries(
            region="USA",
            level=1,
            path=temp_dir
        )
        
        # Verify
        assert result["status"] == "success"
        assert "file_path" in result
        assert "United_States_adm1.geojson" in result["file_path"]
        
        # Verify pygadm was called correctly
        mock_pygadm.AdmItems.assert_called_once_with(
            name="United States",
            content_level=1
        )
        mock_adm_items.to_file.assert_called_once()
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_with_alias(self, mock_pygadm, temp_dir):
        """Test boundary download with country alias."""
        mock_adm_items = MagicMock()
        mock_adm_items.to_file = MagicMock()
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        result = download_boundaries(region="UK", level=0, path=temp_dir)
        
        assert result["status"] == "success"
        # Verify alias was resolved
        mock_pygadm.AdmItems.assert_called_once_with(
            name="United Kingdom",
            content_level=0
        )
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_different_levels(self, mock_pygadm, temp_dir):
        """Test downloading different administrative levels."""
        mock_adm_items = MagicMock()
        mock_adm_items.to_file = MagicMock()
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        # Test level 0 (country)
        result = download_boundaries(region="USA", level=0, path=temp_dir)
        assert result["status"] == "success"
        assert "adm0" in result["file_path"]
        
        # Test level 2 (county)
        result = download_boundaries(region="USA", level=2, path=temp_dir)
        assert result["status"] == "success"
        assert "adm2" in result["file_path"]
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_invalid_region(self, mock_pygadm, temp_dir):
        """Test error handling for invalid region."""
        mock_pygadm.AdmItems.side_effect = Exception("Region not found")
        
        result = download_boundaries(region="INVALID", level=1, path=temp_dir)
        
        assert result["status"] == "error"
        assert "message" in result
        assert "Region not found" in result["message"]
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm', None)
    @patch('gis_mcp.data.administrative_boundaries._pygadm_available', False)
    def test_download_boundaries_pygadm_not_installed(self, temp_dir):
        """Test error when pygadm is not installed."""
        result = download_boundaries(region="USA", level=1, path=temp_dir)
        
        assert result["status"] == "error"
        assert "pygadm is not installed" in result["message"]
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_default_path(self, mock_pygadm, temp_dir):
        """Test boundary download with default storage path."""
        mock_adm_items = MagicMock()
        mock_adm_items.to_file = MagicMock()
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        with patch('gis_mcp.data.administrative_boundaries.get_storage_path') as mock_storage:
            mock_storage.return_value = Path(temp_dir)
            
            result = download_boundaries(region="USA", level=1)
            
            assert result["status"] == "success"
            assert "administrative_boundaries" in result["file_path"]
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_file_write_error(self, mock_pygadm, temp_dir):
        """Test error handling when file write fails."""
        mock_adm_items = MagicMock()
        mock_adm_items.to_file.side_effect = IOError("Permission denied")
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        result = download_boundaries(region="USA", level=1, path=temp_dir)
        
        assert result["status"] == "error"
        assert "Permission denied" in result["message"]
    
    @patch('gis_mcp.data.administrative_boundaries.pygadm')
    def test_download_boundaries_creates_directory(self, mock_pygadm, temp_dir):
        """Test that output directory is created if it doesn't exist."""
        mock_adm_items = MagicMock()
        mock_adm_items.to_file = MagicMock()
        mock_pygadm.AdmItems.return_value = mock_adm_items
        
        nested_path = Path(temp_dir) / "nested" / "path"
        
        result = download_boundaries(region="USA", level=1, path=str(nested_path))
        
        assert result["status"] == "success"
        assert nested_path.exists()
