#!/usr/bin/env python3
"""
Script to list files in the root of Downloads directory by category
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def get_file_category(file_extension):
    """Categorize files based on their extension"""
    categories = {
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        'Presentations': ['.ppt', '.pptx', '.odp'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Executables': ['.exe', '.msi', '.dmg', '.deb', '.rpm'],
        'Code': ['.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c'],
        'Data': ['.json', '.xml', '.sql', '.db', '.sqlite'],
        'System': ['.ini', '.cfg', '.conf', '.log', '.tmp'],
        'Other': []
    }
    
    ext = file_extension.lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return 'Other'

def list_root_files_by_category(directory):
    """List all files in the root directory categorized"""
    print(f"📁 Analyzing root files in: {directory}")
    print("=" * 60)
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return
    
    # Get all items in root directory
    try:
        items = os.listdir(directory)
    except PermissionError:
        print(f"❌ Permission denied: {directory}")
        return
    
    # Separate files from folders
    files = []
    folders = []
    
    for item in items:
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)
    
    # Categorize files
    categorized_files = defaultdict(list)
    total_size = 0
    
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            total_size += file_size_mb
            
            # Get file extension
            _, ext = os.path.splitext(file_name)
            category = get_file_category(ext)
            
            categorized_files[category].append({
                'name': file_name,
                'size_mb': round(file_size_mb, 2),
                'extension': ext
            })
        except (OSError, PermissionError):
            categorized_files['System'].append({
                'name': file_name,
                'size_mb': 0,
                'extension': os.path.splitext(file_name)[1]
            })
    
    # Print summary
    print(f"📊 SUMMARY:")
    print(f"   Total files in root: {len(files)}")
    print(f"   Total folders: {len(folders)}")
    print(f"   Total size: {total_size:.2f} MB")
    print("\n" + "=" * 60)
    
    # Print folders
    if folders:
        print(f"\n📁 FOLDERS ({len(folders)}):")
        for i, folder in enumerate(sorted(folders), 1):
            print(f"   {i:2d}. {folder}")
    
    # Print files by category
    for category in sorted(categorized_files.keys()):
        files_in_category = categorized_files[category]
        if files_in_category:
            category_size = sum(f['size_mb'] for f in files_in_category)
            print(f"\n📄 {category.upper()} ({len(files_in_category)} files, {category_size:.2f} MB):")
            
            # Sort by size (largest first)
            sorted_files = sorted(files_in_category, key=lambda x: x['size_mb'], reverse=True)
            
            for i, file_info in enumerate(sorted_files, 1):
                size_str = f"{file_info['size_mb']:>8.2f} MB" if file_info['size_mb'] > 0 else "      0 MB"
                print(f"   {i:2d}. {size_str} - {file_info['name']}")
    
    # Create JSON report
    report = {
        'directory': directory,
        'summary': {
            'total_files': len(files),
            'total_folders': len(folders),
            'total_size_mb': round(total_size, 2)
        },
        'folders': sorted(folders),
        'files_by_category': dict(categorized_files)
    }
    
    report_file = os.path.join(directory, 'root_files_analysis.json')
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="List root files by category")
    parser.add_argument("directory", nargs='?', default="C:/Users/Admin/Downloads", 
                       help="Directory to analyze (default: Downloads)")
    
    args = parser.parse_args()
    
    try:
        list_root_files_by_category(args.directory)
    except KeyboardInterrupt:
        print("\n👋 Analysis cancelled!")
    except Exception as e:
        print(f"❌ Error: {e}")