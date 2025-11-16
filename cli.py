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
from typing import Optional

from dotenv import load_dotenv

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for better Unicode support
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback: replace problematic Unicode characters
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Add the current directory to the path to import our module
sys.path.insert(0, str(Path(__file__).parent))

from document_controller import DocumentController


async def quick_scan(directory: str, github_token: Optional[str] = None):
    """Perform a quick scan and analysis of a directory"""
    controller = DocumentController(github_token)
    
    if controller.is_online_mode:
        await controller.initialize_agent()
    
    mode_text = "🤖 AI-powered" if controller.is_online_mode else "🔧 Offline"
    print(f"🔍 {mode_text} scan of directory: {directory}")
    
    # Use the agent's tools directly for quick analysis
    scan_result = controller.scan_documents(directory, 5000)
    print("\n📊 Scan Results:")
    print(scan_result)
    
    print("\n🔍 Looking for duplicates...")
    duplicate_result = controller.find_duplicates()
    print(duplicate_result)
    
    print("\n Finding old files...")
    old_files_result = controller.get_old_files(365)
    print(old_files_result)
    
    print("\n💡 Organization suggestions...")
    suggestions = controller.suggest_organization()
    print(suggestions)


async def interactive_mode(github_token: Optional[str] = None):
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
    force_offline = os.getenv("FORCE_OFFLINE", "false").lower() == "true"
    
    if force_offline:
        print("🔧 Forced offline mode enabled")
        github_token = None
    elif not github_token:
        print("⚠️  No GitHub token found - running in offline mode")
        print("💡 Set GITHUB_TOKEN environment variable or use --token argument for AI features")
        print("📖 Get a token from: https://github.com/settings/tokens")
        print("🔧 Continuing with offline capabilities...\n")
    
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