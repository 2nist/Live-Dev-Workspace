"""
Project Manager for organizing songs, arrangements, and musical projects.
Handles project lifecycle, collaboration, and Live set integration.
"""
import os
import logging
import uuid
import shutil
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from pathlib import Path

from ableton_arranger.data.models import (
    ProjectRecord, SongRecord, ProjectStatus, BrowserConfig
)
from ableton_arranger.data.database import DatabaseManager
from ableton_arranger.shared.data_models import AnalysisData
from ableton_arranger.core.connection import LiveConnection


logger = logging.getLogger(__name__)


class ProjectManager:
    """
    Manages music projects containing songs, arrangements, and Live sets.
    Designed for M4L compatibility with simple operations.
    """
    
    def __init__(self, database: DatabaseManager, config: BrowserConfig):
        """
        Initialize project manager.
        
        Args:
            database: Database manager instance
            config: Browser configuration
        """
        self.db = database
        self.config = config
        self.current_project: Optional[ProjectRecord] = None
        
        # Project directories
        self.projects_root = os.path.expanduser("~/Music/ableton_arranger/projects")
        os.makedirs(self.projects_root, exist_ok=True)
    
    def create_project(self, name: str, description: str = "", 
                      template_project_id: Optional[str] = None) -> Optional[ProjectRecord]:
        """
        Create a new music project.
        
        Args:
            name: Project name
            description: Project description
            template_project_id: Optional project to use as template
            
        Returns:
            Created ProjectRecord or None if failed
        """
        try:
            # Generate unique ID
            project_id = f"proj_{uuid.uuid4().hex[:8]}"
            
            # Create project directory
            project_dir = os.path.join(self.projects_root, f"{project_id}_{name}")
            os.makedirs(project_dir, exist_ok=True)
            
            # Create subdirectories
            subdirs = ["audio", "midi", "exports", "references", "notes"]
            for subdir in subdirs:
                os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)
            
            # Initialize project record
            project = ProjectRecord(
                id=project_id,
                name=name,
                description=description,
                status=ProjectStatus.DRAFT
            )
            
            # Copy from template if provided
            if template_project_id:
                template = self.get_project(template_project_id)
                if template:
                    project = self._copy_from_template(project, template)
            
            # Store in database
            if self.db.add_project(project):
                # Create initial Live set
                live_set_path = self._create_initial_live_set(project, project_dir)
                if live_set_path:
                    project.live_set_path = live_set_path
                    self.db.add_project(project)  # Update with Live set path
                
                logger.info(f"Created project: {name} ({project_id})")
                return project
            else:
                # Cleanup on failure
                shutil.rmtree(project_dir, ignore_errors=True)
                return None
                
        except Exception as e:
            logger.error(f"Failed to create project '{name}': {e}")
            return None
    
    def get_project(self, project_id: str) -> Optional[ProjectRecord]:
        """Get project by ID."""
        try:
            import sqlite3
            import json
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()
                
                if row:
                    project_data = dict(row)
                    
                    # Convert JSON fields back
                    import json
                    for field in ['songs', 'arrangements', 'reference_tracks', 'tags', 
                                 'custom_fields', 'collaborators', 'export_paths']:
                        if field in project_data and project_data[field]:
                            if field == 'tags':
                                project_data[field] = set(json.loads(project_data[field]))
                            else:
                                project_data[field] = json.loads(project_data[field])
                    
                    project_data['project_structure'] = json.loads(project_data['project_structure'])
                    
                    # Convert datetime fields
                    for field in ['created_date', 'modified_date', 'last_opened']:
                        if project_data[field]:
                            project_data[field] = datetime.fromisoformat(project_data[field])
                    
                    return ProjectRecord.from_dict(project_data)
                    
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
        
        return None
    
    def open_project(self, project_id: str, connection: Optional[LiveConnection] = None) -> bool:
        """
        Open a project and optionally load its Live set.
        
        Args:
            project_id: Project ID to open
            connection: Optional Live connection for opening Live set
            
        Returns:
            True if successful
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Set as current project
            self.current_project = project
            
            # Update last opened time
            project.last_opened = datetime.now()
            self.db.add_project(project)
            
            # Open Live set if connection provided
            if connection and project.live_set_path and os.path.exists(project.live_set_path):
                success = connection.open_live_set(project.live_set_path)
                if success:
                    logger.info(f"Opened Live set: {project.live_set_path}")
                else:
                    logger.warning("Failed to open Live set")
            
            logger.info(f"Opened project: {project.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open project {project_id}: {e}")
            return False
    
    def add_song_to_project(self, project_id: str, song_id: str) -> bool:
        """Add a song to a project."""
        try:
            project = self.get_project(project_id)
            song = self.db.get_song(song_id)
            
            if not project or not song:
                return False
            
            # Add song ID to project
            if song_id not in project.songs:
                project.songs.append(song_id)
                project.modified_date = datetime.now()
                
                # Update database
                if self.db.add_project(project):
                    logger.info(f"Added song '{song.title}' to project '{project.name}'")
                    return True
            
        except Exception as e:
            logger.error(f"Failed to add song to project: {e}")
        
        return False
    
    def create_arrangement_from_analysis(self, project_id: str, 
                                       analysis_data: AnalysisData,
                                       arrangement_name: str = "") -> Optional[str]:
        """
        Create an arrangement in the project from analysis data.
        
        Args:
            project_id: Target project ID
            analysis_data: Analysis data to create arrangement from
            arrangement_name: Name for the arrangement
            
        Returns:
            Arrangement ID if successful
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return None
            
            # Generate arrangement ID
            arrangement_id = f"arr_{uuid.uuid4().hex[:8]}"
            
            if not arrangement_name:
                arrangement_name = f"Arrangement from {analysis_data.song_info.title}"
            
            # Create arrangement data structure
            arrangement_data = {
                'id': arrangement_id,
                'name': arrangement_name,
                'created_date': datetime.now().isoformat(),
                'source_analysis_id': getattr(analysis_data, 'id', None),
                'sections': [section.__dict__ for section in analysis_data.sections],
                'chords': [chord.__dict__ for chord in analysis_data.chords],
                'tempo': analysis_data.tempo,
                'key_signature': analysis_data.key_signature,
                'time_signature': f"{analysis_data.time_signature_num}/{analysis_data.time_signature_denom}"
            }
            
            # Add arrangement to project
            project.arrangements.append(arrangement_data)
            project.modified_date = datetime.now()
            
            # Update database
            if self.db.add_project(project):
                logger.info(f"Created arrangement '{arrangement_name}' in project '{project.name}'")
                return arrangement_id
            
        except Exception as e:
            logger.error(f"Failed to create arrangement: {e}")
        
        return None
    
    def get_project_songs(self, project_id: str) -> List[SongRecord]:
        """Get all songs in a project."""
        try:
            project = self.get_project(project_id)
            if not project:
                return []
            
            songs = []
            for song_id in project.songs:
                song = self.db.get_song(song_id)
                if song:
                    songs.append(song)
            
            return songs
            
        except Exception as e:
            logger.error(f"Failed to get project songs: {e}")
            return []
    
    def export_project(self, project_id: str, export_format: str = "live_set") -> Optional[str]:
        """
        Export project in various formats.
        
        Args:
            project_id: Project to export
            export_format: Export format (live_set, stems, midi, etc.)
            
        Returns:
            Path to exported file/folder
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return None
            
            # Create export directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_name = f"{project.name}_{export_format}_{timestamp}"
            export_dir = os.path.join(self.projects_root, project_id, "exports", export_name)
            os.makedirs(export_dir, exist_ok=True)
            
            if export_format == "live_set":
                return self._export_live_set(project, export_dir)
            elif export_format == "stems":
                return self._export_stems(project, export_dir)
            elif export_format == "midi":
                return self._export_midi(project, export_dir)
            elif export_format == "analysis_json":
                return self._export_analysis_data(project, export_dir)
            else:
                logger.warning(f"Unknown export format: {export_format}")
                return None
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None
    
    def list_projects(self, status_filter: Optional[ProjectStatus] = None) -> List[ProjectRecord]:
        """List all projects, optionally filtered by status."""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if status_filter:
                    cursor = conn.execute(
                        "SELECT * FROM projects WHERE status = ? ORDER BY modified_date DESC",
                        (status_filter.value,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM projects ORDER BY modified_date DESC"
                    )
                
                projects = []
                for row in cursor.fetchall():
                    project_data = dict(row)
                    
                    # Convert JSON fields
                    import json
                    for field in ['songs', 'arrangements', 'reference_tracks', 'tags', 
                                 'custom_fields', 'collaborators', 'export_paths']:
                        if field in project_data and project_data[field]:
                            if field == 'tags':
                                project_data[field] = set(json.loads(project_data[field]))
                            else:
                                project_data[field] = json.loads(project_data[field])
                    
                    # Convert datetime fields
                    for field in ['created_date', 'modified_date', 'last_opened']:
                        if project_data[field]:
                            project_data[field] = datetime.fromisoformat(project_data[field])
                    
                    projects.append(ProjectRecord.from_dict(project_data))
                
                return projects
                
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def delete_project(self, project_id: str, delete_files: bool = False) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID to delete
            delete_files: Whether to delete project files
            
        Returns:
            True if successful
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Delete from database
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
            
            # Delete files if requested
            if delete_files:
                project_dir = os.path.join(self.projects_root, f"{project_id}_{project.name}")
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
            
            logger.info(f"Deleted project: {project.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False
    
    # Private methods for internal operations
    def _copy_from_template(self, project: ProjectRecord, template: ProjectRecord) -> ProjectRecord:
        """Copy settings from template project."""
        project.default_tempo = template.default_tempo
        project.default_key = template.default_key
        project.default_time_signature = template.default_time_signature
        project.genre = template.genre
        project.project_structure = template.project_structure.copy()
        return project
    
    def _create_initial_live_set(self, project: ProjectRecord, project_dir: str) -> Optional[str]:
        """Create initial Live set for project."""
        try:
            live_set_name = f"{project.name}.als"
            live_set_path = os.path.join(project_dir, live_set_name)
            
            # Create basic Live set template
            # This would require AbletonOSC integration or Live set template
            # For now, just create placeholder
            template_content = self._get_live_set_template(project)
            
            with open(live_set_path, 'w') as f:
                f.write(template_content)
            
            return live_set_path
            
        except Exception as e:
            logger.error(f"Failed to create Live set: {e}")
            return None
    
    def _get_live_set_template(self, project: ProjectRecord) -> str:
        """Get Live set template content."""
        # This would return actual Live set XML template
        # For now, return placeholder
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Ableton Live Set for Project: {project.name} -->
<!-- Created: {project.created_date} -->
<!-- Default Tempo: {project.default_tempo} BPM -->
<!-- Default Key: {project.default_key} -->
<AbletonLiveSet>
    <!-- Live set content would go here -->
</AbletonLiveSet>"""
    
    def _export_live_set(self, project: ProjectRecord, export_dir: str) -> str:
        """Export Live set and project files."""
        if project.live_set_path and os.path.exists(project.live_set_path):
            dest_path = os.path.join(export_dir, os.path.basename(project.live_set_path))
            shutil.copy2(project.live_set_path, dest_path)
            return dest_path
        return export_dir
    
    def _export_stems(self, project: ProjectRecord, export_dir: str) -> str:
        """Export all stems from project songs."""
        # Implementation would collect stems from analyzed songs
        logger.info(f"Exporting stems to: {export_dir}")
        return export_dir
    
    def _export_midi(self, project: ProjectRecord, export_dir: str) -> str:
        """Export all MIDI data from project."""
        # Implementation would collect MIDI from analyzed songs
        logger.info(f"Exporting MIDI to: {export_dir}")
        return export_dir
    
    def _export_analysis_data(self, project: ProjectRecord, export_dir: str) -> str:
        """Export analysis data as JSON."""
        analysis_file = os.path.join(export_dir, "analysis_data.json")
        
        project_analysis = {
            'project': project.to_dict(),
            'songs': [],
            'analysis_data': []
        }
        
        # Collect song and analysis data
        for song_id in project.songs:
            song = self.db.get_song(song_id)
            if song:
                project_analysis['songs'].append(song.to_dict())
                
                analysis = self.db.get_analysis_data(song_id)
                if analysis:
                    project_analysis['analysis_data'].append({
                        'song_id': song_id,
                        'analysis': json.loads(analysis.to_json())
                    })
        
        import json
        with open(analysis_file, 'w') as f:
            json.dump(project_analysis, f, indent=2)
        
        return analysis_file


# Example usage and testing
def create_sample_project(project_manager: ProjectManager) -> Optional[ProjectRecord]:
    """Create a sample project for testing."""
    project = project_manager.create_project(
        name="Sample Electronic Track",
        description="Test project with electronic music elements"
    )
    
    if project:
        # Set project defaults
        project.default_tempo = 128.0
        project.default_key = "Am"
        project.genre = "Electronic"
        project.tags.add("experimental")
        project.tags.add("demo")
        
        # Update in database
        project_manager.db.add_project(project)
        
        logger.info(f"Created sample project: {project.id}")
    
    return project
