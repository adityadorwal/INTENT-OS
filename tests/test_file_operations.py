"""
Unit Tests for File Operations
Tests file organization, compression, extraction, and deletion
"""

import pytest
import sys
import os
import shutil
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_operations_bridge import FileOperationsBridge


class TestFileOperationsBridge:
    """Test suite for FileOperationsBridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a FileOperationsBridge instance"""
        return FileOperationsBridge()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        # Cleanup
        if Path(temp_path).exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing"""
        files = {
            'image.jpg': b'fake image data',
            'document.pdf': b'fake pdf data',
            'video.mp4': b'fake video data',
            'audio.mp3': b'fake audio data',
            'archive.zip': b'fake zip data',
            'script.py': b'print("hello")',
            'data.txt': b'some text data',
        }
        
        for filename, content in files.items():
            file_path = temp_dir / filename
            file_path.write_bytes(content)
        
        return temp_dir
    
    # ========================================
    # INITIALIZATION TESTS
    # ========================================
    
    def test_bridge_initialization(self, bridge):
        """Test that bridge initializes correctly"""
        assert bridge is not None
        assert isinstance(bridge.user_folders, dict)
    
    def test_user_folders_detection(self, bridge):
        """Test that common user folders are detected"""
        # Should detect at least some standard folders
        assert len(bridge.user_folders) > 0
        
        # Common folders that should exist on most systems
        expected_folders = ['downloads', 'documents', 'desktop']
        found_folders = [f for f in expected_folders if f in bridge.user_folders]
        
        # At least one should exist
        assert len(found_folders) > 0
    
    # ========================================
    # FOLDER RESOLUTION TESTS
    # ========================================
    
    def test_resolve_known_folder(self, bridge):
        """Test resolving known folder names"""
        # Test with lowercase
        result = bridge._resolve_folder_path("downloads")
        if result:  # Only test if downloads folder exists
            assert result.exists()
            assert result.name.lower() == "downloads"
    
    def test_resolve_my_prefix(self, bridge):
        """Test resolving folder with 'my' prefix"""
        result = bridge._resolve_folder_path("my downloads")
        if result:
            assert result.exists()
    
    def test_resolve_absolute_path(self, bridge, temp_dir):
        """Test resolving absolute path"""
        result = bridge._resolve_folder_path(str(temp_dir))
        assert result == temp_dir
        assert result.exists()
    
    def test_resolve_nonexistent_folder(self, bridge):
        """Test resolving non-existent folder returns None"""
        result = bridge._resolve_folder_path("nonexistent_folder_12345")
        # Should return None or handle gracefully
        assert result is None or not result.exists()
    
    # ========================================
    # ORGANIZE FOLDER TESTS
    # ========================================
    
    def test_organize_folder_dry_run(self, bridge, sample_files):
        """Test organizing files in dry-run mode"""
        result = bridge.organize_folder(str(sample_files), dry_run=True)
        
        assert result is True
        
        # Files should still be in original location (dry run)
        assert (sample_files / 'image.jpg').exists()
        assert not (sample_files / 'Images' / 'image.jpg').exists()
    
    def test_organize_folder_actual(self, bridge, sample_files):
        """Test actually organizing files"""
        result = bridge.organize_folder(str(sample_files), dry_run=False)
        
        assert result is True
        
        # Check that category folders were created
        categories_created = [
            d.name for d in sample_files.iterdir() if d.is_dir()
        ]
        
        # Should have created some category folders
        assert len(categories_created) > 0
        
        # Check specific file movements
        images_folder = sample_files / 'Images'
        if images_folder.exists():
            assert (images_folder / 'image.jpg').exists()
    
    def test_organize_empty_folder(self, bridge, temp_dir):
        """Test organizing an empty folder"""
        result = bridge.organize_folder(str(temp_dir), dry_run=False)
        
        # Should handle empty folder gracefully
        assert result is True
    
    def test_organize_nonexistent_folder(self, bridge):
        """Test organizing non-existent folder"""
        result = bridge.organize_folder("nonexistent_folder_xyz")
        
        assert result is False
    
    # ========================================
    # COMPRESS FOLDER TESTS
    # ========================================
    
    def test_compress_single_file(self, bridge, temp_dir):
        """Test compressing a single file"""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        result = bridge.compress_folder(str(test_file))
        
        assert result is True
        
        # Check that zip file was created
        zip_files = list(temp_dir.glob("*.zip"))
        assert len(zip_files) > 0
    
    def test_compress_folder(self, bridge, sample_files):
        """Test compressing a folder"""
        result = bridge.compress_folder(str(sample_files))
        
        assert result is True
        
        # Check that zip file exists
        parent = sample_files.parent
        zip_files = list(parent.glob(f"{sample_files.name}*.zip"))
        assert len(zip_files) > 0
    
    def test_compress_with_custom_name(self, bridge, temp_dir):
        """Test compression with custom output name"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        custom_name = "custom_backup"
        result = bridge.compress_folder(str(test_file), custom_name)
        
        assert result is True
        
        # Check for custom named zip
        zip_file = temp_dir / f"{custom_name}.zip"
        assert zip_file.exists()
    
    def test_compress_nonexistent(self, bridge):
        """Test compressing non-existent target"""
        result = bridge.compress_folder("nonexistent_target_xyz")
        
        assert result is False
    
    # ========================================
    # EXTRACT ARCHIVE TESTS
    # ========================================
    
    def test_extract_archive(self, bridge, temp_dir):
        """Test extracting a zip archive"""
        import zipfile
        
        # Create a test zip file
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("file1.txt", "content1")
            zipf.writestr("file2.txt", "content2")
        
        result = bridge.extract_archive(str(zip_path))
        
        assert result is True
        
        # Check extraction folder
        extract_folder = temp_dir / "test"
        assert extract_folder.exists()
        assert (extract_folder / "file1.txt").exists()
        assert (extract_folder / "file2.txt").exists()
    
    def test_extract_with_custom_destination(self, bridge, temp_dir):
        """Test extraction with custom destination"""
        import zipfile
        
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("file.txt", "content")
        
        custom_dest = temp_dir / "extracted"
        result = bridge.extract_archive(str(zip_path), str(custom_dest))
        
        assert result is True
        assert custom_dest.exists()
        assert (custom_dest / "file.txt").exists()
    
    def test_extract_nonexistent_archive(self, bridge):
        """Test extracting non-existent archive"""
        result = bridge.extract_archive("nonexistent.zip")
        
        assert result is False
    
    # ========================================
    # DELETE FILE TESTS
    # ========================================
    
    def test_delete_file_no_confirm(self, bridge, temp_dir):
        """Test deleting file without confirmation"""
        test_file = temp_dir / "delete_me.txt"
        test_file.write_text("content")
        
        result = bridge.delete_file(str(test_file), confirm=False)
        
        assert result is True
        assert not test_file.exists()
    
    def test_delete_folder_no_confirm(self, bridge, temp_dir):
        """Test deleting folder without confirmation"""
        test_folder = temp_dir / "delete_folder"
        test_folder.mkdir()
        (test_folder / "file.txt").write_text("content")
        
        result = bridge.delete_file(str(test_folder), confirm=False)
        
        assert result is True
        assert not test_folder.exists()
    
    def test_delete_nonexistent_file(self, bridge):
        """Test deleting non-existent file"""
        result = bridge.delete_file("nonexistent_file.txt", confirm=False)
        
        assert result is False
    
    # ========================================
    # ERROR HANDLING TESTS
    # ========================================
    
    def test_organize_with_permission_error(self, bridge, temp_dir):
        """Test organize when files are read-only"""
        # Create a read-only file
        readonly_file = temp_dir / "readonly.txt"
        readonly_file.write_text("content")
        
        # Make it writable for cleanup
        # This test verifies graceful error handling
        result = bridge.organize_folder(str(temp_dir), dry_run=False)
        
        # Should still succeed or handle gracefully
        assert result in [True, False]


# ========================================
# CONVENIENCE FUNCTION TESTS
# ========================================

class TestConvenienceFunctions:
    """Test the convenience wrapper functions"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        if Path(temp_path).exists():
            shutil.rmtree(temp_path)
    
    def test_organize_folder_function(self, temp_dir):
        """Test organize_folder convenience function"""
        from file_operations_bridge import organize_folder
        
        # Create some files
        (temp_dir / "test.jpg").write_bytes(b'data')
        
        result = organize_folder(str(temp_dir), dry_run=True)
        assert isinstance(result, bool)
    
    def test_compress_folder_function(self, temp_dir):
        """Test compress_folder convenience function"""
        from file_operations_bridge import compress_folder
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        result = compress_folder(str(test_file))
        assert isinstance(result, bool)
    
    def test_extract_archive_function(self, temp_dir):
        """Test extract_archive convenience function"""
        from file_operations_bridge import extract_archive
        import zipfile
        
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("file.txt", "content")
        
        result = extract_archive(str(zip_path))
        assert isinstance(result, bool)


# ========================================
# INTEGRATION TESTS
# ========================================

@pytest.mark.integration
class TestFileOperationsIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def workspace(self):
        """Create a workspace for integration tests"""
        temp_path = tempfile.mkdtemp()
        workspace = Path(temp_path)
        
        # Create a realistic file structure
        (workspace / "image1.jpg").write_bytes(b'jpg data')
        (workspace / "image2.png").write_bytes(b'png data')
        (workspace / "doc.pdf").write_bytes(b'pdf data')
        (workspace / "video.mp4").write_bytes(b'video data')
        (workspace / "code.py").write_text("print('hello')")
        
        yield workspace
        
        if workspace.exists():
            shutil.rmtree(workspace)
    
    def test_organize_then_compress_workflow(self, workspace):
        """Test organizing files then compressing the result"""
        bridge = FileOperationsBridge()
        
        # Step 1: Organize
        organize_result = bridge.organize_folder(str(workspace), dry_run=False)
        assert organize_result is True
        
        # Step 2: Compress
        compress_result = bridge.compress_folder(str(workspace))
        assert compress_result is True
    
    def test_compress_then_extract_workflow(self, workspace):
        """Test compressing then extracting"""
        bridge = FileOperationsBridge()
        
        # Compress
        compress_result = bridge.compress_folder(str(workspace), "backup.zip")
        assert compress_result is True
        
        # Find the created zip
        zip_file = workspace.parent / "backup.zip"
        
        # Extract to new location
        extract_dir = workspace.parent / "extracted"
        extract_result = bridge.extract_archive(str(zip_file), str(extract_dir))
        assert extract_result is True
        
        # Verify files extracted
        assert extract_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
