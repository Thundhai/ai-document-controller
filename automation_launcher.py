#!/usr/bin/env python3
"""
Simple Automation Launcher

This provides an easy interface to run automation tasks manually or on schedule.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from automation_agent import AutomationScheduler, AutomationConfig


async def run_automation_task(task_type: str):
    """Run a specific automation task"""
    
    # Load configuration
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found in .env file")
        return
    
    # Create configuration
    config = AutomationConfig()
    
    # Load settings from environment
    config.daily_enabled = os.getenv("DAILY_AUTOMATION", "true").lower() == "true"
    config.weekly_enabled = os.getenv("WEEKLY_AUTOMATION", "true").lower() == "true"
    config.monthly_enabled = os.getenv("MONTHLY_AUTOMATION", "true").lower() == "true"
    config.auto_delete_duplicates = os.getenv("AUTO_DELETE_DUPLICATES", "false").lower() == "true"
    config.auto_organize_files = os.getenv("AUTO_ORGANIZE_FILES", "true").lower() == "true"
    config.auto_archive_old_files = os.getenv("AUTO_ARCHIVE_OLD_FILES", "false").lower() == "true"
    
    # Override directories if specified
    monitor_dirs = os.getenv("MONITOR_DIRECTORIES")
    if monitor_dirs:
        config.monitor_directories = [d.strip() for d in monitor_dirs.split(",")]
    
    # Initialize scheduler
    scheduler = AutomationScheduler(config, github_token)
    
    print(f"🤖 Running {task_type} automation task...")
    print("🔄 Initializing AI agent...")
    
    try:
        await scheduler.initialize_agent()
        
        # Run the specified task
        if task_type == "daily":
            report = await scheduler.daily_cleanup()
        elif task_type == "weekly":
            report = await scheduler.weekly_cleanup()
        elif task_type == "monthly":
            report = await scheduler.monthly_cleanup()
        else:
            print(f"❌ Unknown task type: {task_type}")
            return
        
        # Display results
        print(f"\n✅ {task_type.title()} automation completed!")
        print("=" * 50)
        print(f"📊 Results Summary:")
        print(f"   📁 Directories processed: {len(report.directories_processed)}")
        print(f"   📄 Files scanned: {report.files_scanned:,}")
        print(f"   🔄 Duplicates found: {report.duplicates_found}")
        print(f"   🗑️  Duplicates removed: {report.duplicates_removed}")
        print(f"   📂 Files organized: {report.files_organized}")
        print(f"   📦 Files archived: {report.files_archived}")
        print(f"   💾 Space saved: {report.space_saved_mb:.2f} MB")
        print(f"   ⚠️  Errors: {len(report.errors)}")
        
        if report.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in report.errors:
                print(f"   - {error}")
        
        if report.recommendations:
            print(f"\n💡 AI Recommendations:")
            for i, recommendation in enumerate(report.recommendations, 1):
                if recommendation.strip():
                    print(f"   {i}. {recommendation.strip()}")
        
        print(f"\n📝 Report saved in automation_reports/ directory")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function for automation launcher"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Document Controller Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automation_launcher.py daily    # Run daily cleanup
  python automation_launcher.py weekly   # Run weekly organization
  python automation_launcher.py monthly  # Run monthly deep analysis
  python automation_launcher.py schedule # Start continuous scheduler
        """
    )
    
    parser.add_argument(
        "task",
        choices=["daily", "weekly", "monthly", "schedule"],
        help="Automation task to run"
    )
    
    args = parser.parse_args()
    
    if args.task == "schedule":
        # Start continuous scheduler
        from automation_agent import main as start_scheduler
        asyncio.run(start_scheduler())
    else:
        # Run specific task
        asyncio.run(run_automation_task(args.task))


if __name__ == "__main__":
    main()