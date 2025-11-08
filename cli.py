#!/usr/bin/env python3
"""
CLI interface for the AI Document Controller Agent

This script provides a command-line interface for common document management tasks.
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add the current directory to the path to import our module
sys.path.insert(0, str(Path(__file__).parent))

from document_controller import DocumentController


async def quick_scan(directory: str, github_token: str):
    """Perform a quick scan and analysis of a directory"""
    controller = DocumentController(github_token)
    await controller.initialize_agent()
    
    print(f"🔍 Scanning directory: {directory}")
    
    # Use the agent's tools directly for quick analysis
    scan_result = controller.scan_documents(directory, 5000)
    print("\n📊 Scan Results:")
    print(scan_result)
    
    print("\n🔍 Looking for duplicates...")
    duplicate_result = controller.find_duplicates()
    print(duplicate_result)
    
    print("\n💾 Analyzing disk usage...")
    usage_result = controller.analyze_disk_usage()
    print(usage_result)
    
    print("\n📅 Finding old files...")
    old_files_result = controller.get_old_files(365)
    print(old_files_result)
    
    print("\n💡 Organization suggestions...")
    suggestions = controller.suggest_organization()
    print(suggestions)


async def interactive_mode(github_token: str):
    """Run interactive mode"""
    controller = DocumentController(github_token)
    await controller.run_interactive_session()


async def main():
    """Main CLI function"""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="AI Document Controller Agent - Intelligent document management"
    )
    
    parser.add_argument(
        "--mode",
        choices=["interactive", "scan"],
        default="interactive",
        help="Mode to run the agent in"
    )
    
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory to scan (required for scan mode)"
    )
    
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub token (or set GITHUB_TOKEN environment variable)"
    )
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = args.token or os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GitHub token is required")
        print("Set GITHUB_TOKEN environment variable or use --token argument")
        print("Get a token from: https://github.com/settings/tokens")
        sys.exit(1)
    
    try:
        if args.mode == "scan":
            if not args.directory:
                print("❌ Error: --directory is required for scan mode")
                sys.exit(1)
            
            if not os.path.exists(args.directory):
                print(f"❌ Error: Directory not found: {args.directory}")
                sys.exit(1)
            
            await quick_scan(args.directory, github_token)
            
        else:  # interactive mode
            await interactive_mode(github_token)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())