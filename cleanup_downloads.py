#!/usr/bin/env python3
"""
Script to implement the recommended cleanup for Downloads folder
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def create_folders_if_needed(base_dir):
    """Create organization folders if they don't exist"""
    folders_to_create = [
        "Archives",
        "Config_Settings", 
        "Documentation",
        "Temp_Cleanup"
    ]
    
    created_folders = []
    for folder in folders_to_create:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            created_folders.append(folder)
            print(f"📁 Created folder: {folder}")
    
    return created_folders

def cleanup_downloads(downloads_dir):
    """Perform the recommended cleanup operations"""
    print(f"🧹 Starting recommended cleanup for: {downloads_dir}")
    print("=" * 60)
    
    if not os.path.exists(downloads_dir):
        print(f"❌ Directory not found: {downloads_dir}")
        return
    
    # Create necessary folders
    created_folders = create_folders_if_needed(downloads_dir)
    
    cleanup_report = {
        "timestamp": datetime.now().isoformat(),
        "actions_performed": [],
        "space_reclaimed_mb": 0,
        "files_moved": 0,
        "files_deleted": 0,
        "created_folders": created_folders
    }
    
    # 1. Move large archives to Archives folder
    print("\n📦 MOVING LARGE ARCHIVES...")
    large_archives = [
        "IT5DSETWin_11200EN.zip",
        "IT5PCL6Winx64_11200EN.zip",
        "Python-3.10.13.tar.xz"
    ]
    
    archives_folder = os.path.join(downloads_dir, "Archives")
    for archive in large_archives:
        source_path = os.path.join(downloads_dir, archive)
        if os.path.exists(source_path):
            dest_path = os.path.join(archives_folder, archive)
            try:
                shutil.move(source_path, dest_path)
                file_size = os.path.getsize(dest_path) / (1024 * 1024)
                print(f"   ✅ Moved: {archive} ({file_size:.1f} MB)")
                cleanup_report["actions_performed"].append(f"Moved {archive} to Archives")
                cleanup_report["files_moved"] += 1
            except Exception as e:
                print(f"   ❌ Error moving {archive}: {e}")
    
    # 2. Delete temporary Word files
    print("\n🗑️  DELETING TEMPORARY FILES...")
    temp_files = [
        "~WRL0374.tmp",
        "~WRL0044.tmp", 
        "~WRL2588.tmp",
        "~WRL0134.tmp"
    ]
    
    for temp_file in temp_files:
        temp_path = os.path.join(downloads_dir, temp_file)
        if os.path.exists(temp_path):
            try:
                file_size = os.path.getsize(temp_path) / (1024 * 1024)
                os.remove(temp_path)
                print(f"   ✅ Deleted: {temp_file} ({file_size:.2f} MB)")
                cleanup_report["actions_performed"].append(f"Deleted temporary file {temp_file}")
                cleanup_report["space_reclaimed_mb"] += file_size
                cleanup_report["files_deleted"] += 1
            except Exception as e:
                print(f"   ❌ Error deleting {temp_file}: {e}")
    
    # 3. Move JSON config files to Config_Settings folder
    print("\n⚙️  ORGANIZING CONFIG FILES...")
    json_files = [
        "Memory Chatbot.json",
        "agentlink-4s83r-firebase-adminsdk-fbsvc-6e5ffd429d.json",
        "ai_structural_review_workflow.json",
        "alm-hse-c71df6ae02b5.json",
        "client_secret_824406281951-nkggicegile9ug6dpb42rvuo2rdqvglv.apps.googleusercontent.com.json",
        "firebase_key.json",
        "flows.json",
        "kaggle.json", 
        "langflow_safety_assistant.json",
        "langflow_safety_assistant_fixed.json",
        "tech-ai-team-7aac37f01ef2.json"
    ]
    
    config_folder = os.path.join(downloads_dir, "Config_Settings")
    for json_file in json_files:
        source_path = os.path.join(downloads_dir, json_file)
        if os.path.exists(source_path):
            dest_path = os.path.join(config_folder, json_file)
            try:
                shutil.move(source_path, dest_path)
                print(f"   ✅ Moved: {json_file}")
                cleanup_report["actions_performed"].append(f"Moved {json_file} to Config_Settings")
                cleanup_report["files_moved"] += 1
            except Exception as e:
                print(f"   ❌ Error moving {json_file}: {e}")
    
    # 4. Move README and documentation files
    print("\n📚 ORGANIZING DOCUMENTATION...")
    doc_files = [
        "README(1).md",
        "README(2).md", 
        "README(3).md",
        "README.md",
        "README_Tech_AI_Team.md",
        "README_with_limitations.md",
        "adk.yaml",
        "agent.yaml",
        "workflow.dot"
    ]
    
    doc_folder = os.path.join(downloads_dir, "Documentation")
    for doc_file in doc_files:
        source_path = os.path.join(downloads_dir, doc_file)
        if os.path.exists(source_path):
            dest_path = os.path.join(doc_folder, doc_file)
            try:
                shutil.move(source_path, dest_path)
                print(f"   ✅ Moved: {doc_file}")
                cleanup_report["actions_performed"].append(f"Moved {doc_file} to Documentation")
                cleanup_report["files_moved"] += 1
            except Exception as e:
                print(f"   ❌ Error moving {doc_file}: {e}")
    
    # 5. Move miscellaneous files to Temp_Cleanup for review
    print("\n🔍 MOVING MISCELLANEOUS FILES FOR REVIEW...")
    misc_files = [
        "cellar_345ba795-828f-11ee-99ba-01aa75ed71a1.xml",
        "Portfolio Project - EDA.sql",
        "a5ed61ee-0714-46e9-a11e-96992b08ebde",
        "0a450945-d903-4c85-902f-a584dd926071",
        "Recording.m4a",
        "risk_classifier.joblib",
        "OIP-3254437492.XOyLHdoJTe5Lx7qmK3vS8gHaFS",
        "OIP-4247407158.AoWMHEKZv2G3ZlJBJ1Er-AHaHa",
        "WhatsApp Audio 2025-07-05 at 04.07.42_bf9b29f6.dat.unknown"
    ]
    
    temp_folder = os.path.join(downloads_dir, "Temp_Cleanup")
    for misc_file in misc_files:
        source_path = os.path.join(downloads_dir, misc_file)
        if os.path.exists(source_path):
            dest_path = os.path.join(temp_folder, misc_file)
            try:
                shutil.move(source_path, dest_path)
                file_size = os.path.getsize(dest_path) / (1024 * 1024)
                print(f"   ✅ Moved: {misc_file} ({file_size:.2f} MB)")
                cleanup_report["actions_performed"].append(f"Moved {misc_file} to Temp_Cleanup")
                cleanup_report["files_moved"] += 1
            except Exception as e:
                print(f"   ❌ Error moving {misc_file}: {e}")
    
    # Save cleanup report
    report_file = os.path.join(downloads_dir, "cleanup_report.json")
    try:
        with open(report_file, 'w') as f:
            json.dump(cleanup_report, f, indent=2)
        print(f"\n💾 Cleanup report saved: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save cleanup report: {e}")
    
    # Print summary
    print(f"\n✅ CLEANUP COMPLETE!")
    print(f"📊 Summary:")
    print(f"   Files moved: {cleanup_report['files_moved']}")
    print(f"   Files deleted: {cleanup_report['files_deleted']}")
    print(f"   Space reclaimed: {cleanup_report['space_reclaimed_mb']:.2f} MB")
    print(f"   Folders created: {len(cleanup_report['created_folders'])}")
    print(f"\n📁 New folder structure:")
    for folder in cleanup_report['created_folders']:
        print(f"   📁 {folder}/")
    
    return cleanup_report

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup Downloads folder as recommended")
    parser.add_argument("directory", nargs='?', default="C:/Users/Admin/Downloads",
                       help="Downloads directory to cleanup")
    
    args = parser.parse_args()
    
    try:
        cleanup_downloads(args.directory)
    except KeyboardInterrupt:
        print("\n👋 Cleanup cancelled!")
    except Exception as e:
        print(f"❌ Error: {e}")