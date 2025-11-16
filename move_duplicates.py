#!/usr/bin/env python3
"""
Script to move duplicate files to a review folder
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add the current directory to the path to import our module
sys.path.insert(0, str(Path(__file__).parent))

from document_controller import DocumentController


def create_review_folder(base_directory: str) -> str:
    """Create the review_duplicate folder in the base directory"""
    review_folder = os.path.join(base_directory, "review_duplicate")
    os.makedirs(review_folder, exist_ok=True)
    return review_folder


def move_duplicate_files(directory: str):
    """Move duplicate files to review_duplicate folder"""
    print(f"🔍 Analyzing duplicates in: {directory}")
    
    # Initialize the controller to get duplicate analysis
    controller = DocumentController()
    
    # Scan the directory first
    print("📁 Scanning directory...")
    scan_result = controller.scan_documents(directory, 5000)
    
    # Get duplicate analysis
    print("🔍 Finding duplicates...")
    duplicate_result = controller.find_duplicates()
    
    # Parse the JSON result
    try:
        # Remove any prefix text and get just the JSON
        json_str = duplicate_result
        if "Duplicate Analysis:" in json_str:
            json_str = json_str.split("Duplicate Analysis:")[-1].strip()
        
        duplicate_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing duplicate data: {e}")
        print(f"Raw data: {duplicate_result[:200]}...")
        return
    
    # Create review folder
    review_folder = create_review_folder(directory)
    print(f"📁 Created review folder: {review_folder}")
    
    moved_files = 0
    total_size_saved = 0
    
    # Process each duplicate group
    for group in duplicate_data.get("examples", []):
        files = group.get("files", [])
        if len(files) < 2:
            continue
            
        # Keep the first file, move the rest to review folder
        original_file = files[0]
        duplicates = files[1:]
        
        print(f"\n📄 Processing: {original_file['name']}")
        print(f"   Keeping: {original_file['path']}")
        
        for i, duplicate in enumerate(duplicates):
            try:
                source_path = duplicate['path']
                if not os.path.exists(source_path):
                    print(f"   ⚠️  File not found: {source_path}")
                    continue
                
                # Create unique name for moved file
                base_name = duplicate['name']
                name_parts = os.path.splitext(base_name)
                new_name = f"{name_parts[0]}_duplicate_{i+1}{name_parts[1]}"
                dest_path = os.path.join(review_folder, new_name)
                
                # Move the file
                shutil.move(source_path, dest_path)
                file_size = os.path.getsize(dest_path) / (1024 * 1024)  # MB
                total_size_saved += file_size
                moved_files += 1
                
                print(f"   ✅ Moved: {base_name} → {new_name}")
                
            except Exception as e:
                print(f"   ❌ Error moving {duplicate['path']}: {e}")
    
    # Create summary file
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files_moved": moved_files,
        "total_size_mb": round(total_size_saved, 2),
        "review_folder": review_folder,
        "original_directory": directory
    }
    
    summary_file = os.path.join(review_folder, "duplicate_move_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Duplicate cleanup complete!")
    print(f"📊 Files moved: {moved_files}")
    print(f"💾 Space organized: {total_size_saved:.2f} MB")
    print(f"📁 Review folder: {review_folder}")
    print(f"📋 Summary saved: {summary_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Move duplicate files to review folder")
    parser.add_argument("directory", help="Directory to process for duplicates")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ Error: Directory not found: {args.directory}")
        sys.exit(1)
    
    try:
        move_duplicate_files(args.directory)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)