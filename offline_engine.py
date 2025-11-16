#!/usr/bin/env python3
"""
Offline Recommendations Engine

This module provides rule-based recommendations for document management
when internet connectivity is not available or AI features are disabled.

Author: AI Assistant  
Version: 1.0.0
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class OfflineRecommendationEngine:
    """Provides rule-based recommendations without requiring AI/internet"""
    
    def __init__(self):
        self.file_type_categories = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.wma', '.ogg'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.h', '.php', '.rb'],
            'executables': ['.exe', '.msi', '.dmg', '.deb', '.rpm', '.app']
        }
        
        self.organization_rules = {
            'by_type': 'Organize files into folders by file type',
            'by_date': 'Create date-based folder structure (YYYY/MM)',
            'by_size': 'Separate large files (>100MB) into dedicated folders',
            'by_age': 'Move old files (>1 year) to archive folders'
        }
    
    def analyze_file_distribution(self, documents: List) -> Dict[str, Any]:
        """Analyze file distribution and provide basic insights"""
        if not documents:
            return {"error": "No documents to analyze"}
        
        # Basic statistics
        total_files = len(documents)
        total_size = sum(doc.size for doc in documents)
        
        # File type distribution
        type_distribution = defaultdict(int)
        size_by_type = defaultdict(int)
        
        for doc in documents:
            category = self._get_file_category(doc.extension)
            type_distribution[category] += 1
            size_by_type[category] += doc.size
        
        # Date analysis
        now = datetime.now()
        age_distribution = {
            'very_recent': 0,  # < 1 week
            'recent': 0,       # < 1 month
            'old': 0,          # < 1 year
            'very_old': 0      # > 1 year
        }
        
        for doc in documents:
            age_days = (now - doc.modified_date).days
            if age_days < 7:
                age_distribution['very_recent'] += 1
            elif age_days < 30:
                age_distribution['recent'] += 1
            elif age_days < 365:
                age_distribution['old'] += 1
            else:
                age_distribution['very_old'] += 1
        
        # Size analysis
        large_files = [doc for doc in documents if doc.size > 100 * 1024 * 1024]  # > 100MB
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "type_distribution": dict(type_distribution),
            "size_by_type_mb": {k: round(v / (1024 * 1024), 2) for k, v in size_by_type.items()},
            "age_distribution": age_distribution,
            "large_files_count": len(large_files),
            "avg_file_size_kb": round(total_size / total_files / 1024, 2) if total_files > 0 else 0
        }
    
    def suggest_organization_strategy(self, documents: List) -> List[str]:
        """Provide rule-based organization suggestions"""
        if not documents:
            return ["No documents to organize"]
        
        analysis = self.analyze_file_distribution(documents)
        suggestions = []
        
        # Type-based organization
        if len(analysis['type_distribution']) > 1:
            suggestions.append(
                f"📁 Create {len(analysis['type_distribution'])} folders by file type: " +
                ", ".join(analysis['type_distribution'].keys())
            )
        
        # Date-based organization for large collections
        if analysis['total_files'] > 100:
            suggestions.append(
                "📅 Use date-based organization (YYYY/MM structure) for better navigation"
            )
        
        # Large file management
        if analysis['large_files_count'] > 0:
            suggestions.append(
                f"📦 Move {analysis['large_files_count']} large files (>100MB) to dedicated 'Large Files' folder"
            )
        
        # Old file archival
        if analysis['age_distribution']['very_old'] > 0:
            suggestions.append(
                f"📚 Archive {analysis['age_distribution']['very_old']} old files (>1 year) to 'Archive' folder"
            )
        
        # Cleanup suggestions
        if analysis['total_files'] > 1000:
            suggestions.append(
                "🧹 Consider breaking down large collections into smaller, themed folders"
            )
        
        # Size optimization
        dominant_type = max(analysis['size_by_type_mb'].items(), key=lambda x: x[1])
        if dominant_type[1] > 1000:  # > 1GB
            suggestions.append(
                f"💾 {dominant_type[0]} files use {dominant_type[1]:.1f}MB - consider compression or cloud storage"
            )
        
        return suggestions[:5] if suggestions else ["Files appear well organized"]
    
    def generate_duplicate_strategy(self, duplicates: Dict) -> List[str]:
        """Provide rule-based duplicate cleanup strategy"""
        if not duplicates:
            return ["No duplicates found"]
        
        total_groups = len(duplicates)
        total_duplicates = sum(len(group) - 1 for group in duplicates.values())
        
        strategies = [
            f"🔄 Found {total_groups} groups with {total_duplicates} duplicate files",
        ]
        
        # Size-based strategy
        large_duplicates = []
        small_duplicates = []
        
        for hash_val, docs in duplicates.items():
            if docs[0].size > 10 * 1024 * 1024:  # > 10MB
                large_duplicates.append((hash_val, docs))
            else:
                small_duplicates.append((hash_val, docs))
        
        if large_duplicates:
            strategies.append(
                f"🎯 Priority: Remove {len(large_duplicates)} large duplicate groups first"
            )
        
        strategies.extend([
            "📋 Keep the newest version of each duplicate",
            "🗑️ Delete duplicates from Downloads folder first (likely temporary)",
            "⚠️ Review duplicates in Documents folder manually",
            "💾 Consider compression before deletion for important files"
        ])
        
        return strategies
    
    def suggest_automation_rules(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest automation rules based on file patterns"""
        rules = []
        
        # Auto-organization rules
        if analysis.get('total_files', 0) > 200:
            rules.append(
                "🤖 Enable automatic file organization by type for new files"
            )
        
        # Cleanup automation
        if analysis.get('age_distribution', {}).get('very_old', 0) > 50:
            rules.append(
                "📅 Set up monthly automation to archive files older than 1 year"
            )
        
        # Duplicate prevention
        rules.extend([
            "🔄 Enable weekly duplicate scanning in Downloads folder",
            "📁 Auto-move downloads to type-specific folders after 7 days",
            "🗑️ Auto-delete empty folders during monthly cleanup"
        ])
        
        # Size management
        if analysis.get('total_size_mb', 0) > 10000:  # > 10GB
            rules.append(
                "💾 Set up monthly large file reports for space management"
            )
        
        return rules
    
    def generate_offline_chat_response(self, user_input: str, last_analysis: Dict = None) -> str:
        """Generate rule-based responses to common user queries"""
        user_input_lower = user_input.lower()
        
        # Organization help
        if any(word in user_input_lower for word in ['organize', 'organization', 'structure']):
            return (
                "📁 **Offline Organization Guide:**\n"
                "1. **By Type**: Create folders like Documents/, Images/, Videos/\n"
                "2. **By Date**: Use YYYY/MM structure for chronological organization\n"
                "3. **By Project**: Group related files into project-specific folders\n"
                "4. **By Frequency**: Keep frequently used files in easy-access locations\n\n"
                "💡 Start with type-based organization, then add date structure within each type."
            )
        
        # Cleanup help
        elif any(word in user_input_lower for word in ['clean', 'cleanup', 'delete']):
            return (
                "🧹 **Offline Cleanup Strategy:**\n"
                "1. **Remove duplicates**: Keep newest versions, delete others\n"
                "2. **Archive old files**: Move files >1 year to Archive/ folder\n"
                "3. **Clear Downloads**: Organize or delete downloaded files\n"
                "4. **Empty folders**: Remove folders with no files\n"
                "5. **Large files**: Review files >100MB for compression/deletion\n\n"
                "⚠️ Always backup important files before deleting!"
            )
        
        # Duplicate help
        elif any(word in user_input_lower for word in ['duplicate', 'copies']):
            return (
                "🔄 **Offline Duplicate Management:**\n"
                "1. **Identify**: Use file hashing to find exact duplicates\n"
                "2. **Prioritize**: Handle large duplicates first for space savings\n"
                "3. **Keep newest**: Preserve most recently modified versions\n"
                "4. **Safe locations**: Be careful with duplicates in Documents/\n"
                "5. **Automation**: Set up weekly duplicate scans\n\n"
                "📊 Focus on Downloads and temp folders for safe cleanup."
            )
        
        # General help
        else:
            if last_analysis:
                files_count = last_analysis.get('total_files', 0)
                size_mb = last_analysis.get('total_size_mb', 0)
                return (
                    f"📊 **Current Analysis** ({files_count} files, {size_mb:.1f}MB):\n"
                    "• Scan directories using the scan_documents tool\n"
                    "• Find duplicates to free up space\n"
                    "• Get organization suggestions\n"
                    "• Analyze disk usage by file type\n\n"
                    "💡 **Offline Mode**: Basic file management available without internet."
                )
            else:
                return (
                    "🤖 **AI Document Controller - Offline Mode**\n\n"
                    "Available offline features:\n"
                    "• 📁 Directory scanning and analysis\n"
                    "• 🔄 Duplicate file detection\n" 
                    "• 📊 File type and size analysis\n"
                    "• 📅 Old file identification\n"
                    "• 🗂️ Basic organization suggestions\n\n"
                    "💡 Ask me to scan a directory to get started!"
                )
    
    def _get_file_category(self, extension: str) -> str:
        """Get file category based on extension"""
        extension = extension.lower()
        for category, extensions in self.file_type_categories.items():
            if extension in extensions:
                return category
        return 'other'


# Utility functions for offline mode
def test_internet_connectivity() -> bool:
    """Test if internet connection is available"""
    try:
        import urllib.request
        urllib.request.urlopen('https://models.github.ai', timeout=3)
        return True
    except:
        return False


def get_offline_disk_usage_summary(directory: str) -> Dict[str, Any]:
    """Get disk usage summary without AI analysis"""
    try:
        total_size = 0
        file_count = 0
        type_sizes = defaultdict(int)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    total_size += size
                    file_count += 1
                    
                    ext = Path(file).suffix.lower()
                    type_sizes[ext or 'no_extension'] += size
                    
                except Exception:
                    continue
        
        # Sort by size
        sorted_types = sorted(type_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "directory": directory,
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "top_file_types": [
                {"type": ext, "size_mb": round(size / (1024 * 1024), 2)}
                for ext, size in sorted_types
            ]
        }
        
    except Exception as e:
        return {"error": f"Failed to analyze directory: {e}"}