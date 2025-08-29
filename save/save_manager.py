"""
Save and load system for the pseudo-3D RPG.
Handles game state serialization and persistence.
"""

import json
import os
from datetime import datetime
import pickle
import gzip

class SaveManager:
    def __init__(self):
        """Initialize the save manager."""
        self.save_directory = "saves"
        self.save_extension = ".sav"
        self.backup_extension = ".bak"
        
        # Ensure save directory exists
        self.ensure_save_directory()
        
        # Compression settings
        self.use_compression = True
        self.use_binary = True  # Use pickle for better performance with large data
        
        # Save file versioning
        self.save_version = "1.0"
    
    def ensure_save_directory(self):
        """Create save directory if it doesn't exist."""
        if not os.path.exists(self.save_directory):
            try:
                os.makedirs(self.save_directory)
                print(f"Created save directory: {self.save_directory}")
            except OSError as e:
                print(f"Error creating save directory: {e}")
                # Fallback to current directory
                self.save_directory = "."
    
    def get_save_path(self, save_name):
        """Get the full path for a save file."""
        return os.path.join(self.save_directory, f"{save_name}{self.save_extension}")
    
    def get_backup_path(self, save_name):
        """Get the backup path for a save file."""
        return os.path.join(self.save_directory, f"{save_name}{self.backup_extension}")
    
    def save_game(self, save_name, game_data):
        """Save game data to file."""
        save_path = self.get_save_path(save_name)
        backup_path = self.get_backup_path(save_name)
        
        try:
            # Create backup if save file already exists
            if os.path.exists(save_path):
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(save_path, backup_path)
                print(f"Created backup: {backup_path}")
            
            # Prepare save data with metadata
            save_data = {
                'version': self.save_version,
                'timestamp': datetime.now().isoformat(),
                'game_data': game_data
            }
            
            # Save the data
            if self.use_binary:
                self._save_binary(save_path, save_data)
            else:
                self._save_json(save_path, save_data)
            
            print(f"Game saved successfully: {save_path}")
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            
            # Restore backup if save failed
            if os.path.exists(backup_path):
                try:
                    os.rename(backup_path, save_path)
                    print("Restored backup after save failure")
                except Exception as restore_error:
                    print(f"Error restoring backup: {restore_error}")
            
            return False
    
    def _save_binary(self, file_path, data):
        """Save data using pickle with optional compression."""
        if self.use_compression:
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _save_json(self, file_path, data):
        """Save data as JSON with optional compression."""
        json_str = json.dumps(data, indent=2, default=self._json_serializer)
        
        if self.use_compression:
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-standard types."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def load_game(self, save_name):
        """Load game data from file."""
        save_path = self.get_save_path(save_name)
        
        if not os.path.exists(save_path):
            print(f"Save file not found: {save_path}")
            return None
        
        try:
            # Load the data
            if self.use_binary:
                save_data = self._load_binary(save_path)
            else:
                save_data = self._load_json(save_path)
            
            # Validate save data
            if not self._validate_save_data(save_data):
                print("Invalid save data format")
                return None
            
            # Check version compatibility
            if not self._is_version_compatible(save_data.get('version', '1.0')):
                print(f"Incompatible save version: {save_data.get('version', '1.0')}")
                return None
            
            print(f"Game loaded successfully: {save_path}")
            return save_data['game_data']
            
        except Exception as e:
            print(f"Error loading game: {e}")
            
            # Try to load backup
            backup_path = self.get_backup_path(save_name)
            if os.path.exists(backup_path):
                print("Attempting to load backup...")
                try:
                    if self.use_binary:
                        save_data = self._load_binary(backup_path)
                    else:
                        save_data = self._load_json(backup_path)
                    
                    if self._validate_save_data(save_data):
                        print("Backup loaded successfully")
                        return save_data['game_data']
                except Exception as backup_error:
                    print(f"Error loading backup: {backup_error}")
            
            return None
    
    def _load_binary(self, file_path):
        """Load data using pickle with optional compression."""
        if self.use_compression:
            with gzip.open(file_path, 'rb') as f:
                return pickle.load(f)
        else:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
    
    def _load_json(self, file_path):
        """Load data from JSON with optional compression."""
        if self.use_compression:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _validate_save_data(self, save_data):
        """Validate the structure of save data."""
        if not isinstance(save_data, dict):
            return False
        
        required_keys = ['version', 'timestamp', 'game_data']
        for key in required_keys:
            if key not in save_data:
                return False
        
        return True
    
    def _is_version_compatible(self, save_version):
        """Check if save version is compatible with current version."""
        # For now, only exact version match
        return save_version == self.save_version
    
    def list_saves(self):
        """List all available save files."""
        saves = []
        
        if not os.path.exists(self.save_directory):
            return saves
        
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith(self.save_extension):
                    save_name = filename[:-len(self.save_extension)]
                    save_path = os.path.join(self.save_directory, filename)
                    
                    # Get file info
                    stat = os.stat(save_path)
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Try to get save metadata
                    save_info = {
                        'name': save_name,
                        'path': save_path,
                        'size': file_size,
                        'modified': modified_time,
                        'timestamp': None,
                        'version': None
                    }
                    
                    try:
                        # Load metadata without loading full game data
                        if self.use_binary:
                            data = self._load_binary(save_path)
                        else:
                            data = self._load_json(save_path)
                        
                        save_info['timestamp'] = data.get('timestamp')
                        save_info['version'] = data.get('version')
                    except Exception:
                        # If we can't read metadata, that's okay
                        pass
                    
                    saves.append(save_info)
            
            # Sort by modified time (newest first)
            saves.sort(key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            print(f"Error listing saves: {e}")
        
        return saves
    
    def delete_save(self, save_name):
        """Delete a save file and its backup."""
        save_path = self.get_save_path(save_name)
        backup_path = self.get_backup_path(save_name)
        
        deleted = False
        
        # Delete main save file
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                print(f"Deleted save: {save_path}")
                deleted = True
            except Exception as e:
                print(f"Error deleting save: {e}")
        
        # Delete backup file
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
                print(f"Deleted backup: {backup_path}")
            except Exception as e:
                print(f"Error deleting backup: {e}")
        
        return deleted
    
    def save_exists(self, save_name):
        """Check if a save file exists."""
        return os.path.exists(self.get_save_path(save_name))
    
    def get_save_info(self, save_name):
        """Get information about a specific save file."""
        save_path = self.get_save_path(save_name)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            # Get file stats
            stat = os.stat(save_path)
            
            info = {
                'name': save_name,
                'path': save_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'timestamp': None,
                'version': None,
                'has_backup': os.path.exists(self.get_backup_path(save_name))
            }
            
            # Try to get metadata
            try:
                if self.use_binary:
                    data = self._load_binary(save_path)
                else:
                    data = self._load_json(save_path)
                
                info['timestamp'] = data.get('timestamp')
                info['version'] = data.get('version')
            except Exception:
                # If we can't read metadata, that's okay
                pass
            
            return info
            
        except Exception as e:
            print(f"Error getting save info: {e}")
            return None
    
    def export_save(self, save_name, export_path):
        """Export a save file to a different location."""
        save_path = self.get_save_path(save_name)
        
        if not os.path.exists(save_path):
            print(f"Save file not found: {save_path}")
            return False
        
        try:
            with open(save_path, 'rb') as src:
                with open(export_path, 'wb') as dst:
                    dst.write(src.read())
            
            print(f"Save exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting save: {e}")
            return False
    
    def import_save(self, import_path, save_name):
        """Import a save file from another location."""
        if not os.path.exists(import_path):
            print(f"Import file not found: {import_path}")
            return False
        
        save_path = self.get_save_path(save_name)
        
        try:
            # Validate the import file first
            if self.use_binary:
                test_data = self._load_binary(import_path)
            else:
                test_data = self._load_json(import_path)
            
            if not self._validate_save_data(test_data):
                print("Invalid save file format")
                return False
            
            # Copy the file
            with open(import_path, 'rb') as src:
                with open(save_path, 'wb') as dst:
                    dst.write(src.read())
            
            print(f"Save imported as: {save_name}")
            return True
            
        except Exception as e:
            print(f"Error importing save: {e}")
            return False
    
    def create_autosave(self, game_data, slot=0):
        """Create an autosave in a specific slot."""
        autosave_name = f"autosave_{slot}"
        return self.save_game(autosave_name, game_data)
    
    def load_autosave(self, slot=0):
        """Load an autosave from a specific slot."""
        autosave_name = f"autosave_{slot}"
        return self.load_game(autosave_name)
    
    def cleanup_old_saves(self, keep_count=10):
        """Clean up old save files, keeping only the most recent ones."""
        saves = self.list_saves()
        
        # Filter out autosaves and manual saves separately
        regular_saves = [s for s in saves if not s['name'].startswith('autosave_')]
        autosaves = [s for s in saves if s['name'].startswith('autosave_')]
        
        # Clean up regular saves
        if len(regular_saves) > keep_count:
            old_saves = regular_saves[keep_count:]
            for save in old_saves:
                self.delete_save(save['name'])
                print(f"Cleaned up old save: {save['name']}")
        
        # Keep only the most recent autosave of each slot
        autosave_slots = {}
        for save in autosaves:
            slot = save['name']
            if slot not in autosave_slots or save['modified'] > autosave_slots[slot]['modified']:
                if slot in autosave_slots:
                    # Delete the older autosave
                    self.delete_save(autosave_slots[slot]['name'])
                autosave_slots[slot] = save
    
    def get_total_save_size(self):
        """Get the total size of all save files."""
        total_size = 0
        
        if not os.path.exists(self.save_directory):
            return total_size
        
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith(self.save_extension) or filename.endswith(self.backup_extension):
                    file_path = os.path.join(self.save_directory, filename)
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"Error calculating save size: {e}")
        
        return total_size
