#!/usr/bin/env python3
"""
AI Document Controller Automation Agent

This module provides automated document management with configurable schedules:
- Daily: Quick cleanup and duplicate detection
- Weekly: Full folder organization and old file archival
- Monthly: Deep analysis and storage optimization

Author: AI Assistant
Version: 2.0.0
"""

import asyncio
import json
import os
import hashlib
import shutil
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AutomationConfig:
    """Configuration for automation schedules"""
    daily_enabled: bool = True
    weekly_enabled: bool = True
    monthly_enabled: bool = True
    
    # Directories to monitor
    monitor_directories: List[str] = None
    
    # Automation settings
    auto_delete_duplicates: bool = False
    auto_organize_files: bool = True
    auto_archive_old_files: bool = False
    
    # Thresholds
    old_file_threshold_days: int = 365
    duplicate_size_threshold_mb: int = 1  # Only process duplicates larger than this
    
    # Notification settings
    send_reports: bool = True
    report_email: Optional[str] = None

    def __post_init__(self):
        if self.monitor_directories is None:
            # Default directories
            user_profile = os.path.expanduser("~")
            self.monitor_directories = [
                os.path.join(user_profile, "Downloads"),
                os.path.join(user_profile, "Documents"),
                os.path.join(user_profile, "Desktop")
            ]


@dataclass
class AutomationReport:
    """Report structure for automation runs"""
    timestamp: datetime
    task_type: str  # daily, weekly, monthly
    directories_processed: List[str]
    files_scanned: int
    duplicates_found: int
    duplicates_removed: int
    files_organized: int
    files_archived: int
    space_saved_mb: float
    errors: List[str]
    recommendations: List[str]


class AutomationScheduler:
    """Handles scheduling and execution of automation tasks"""
    
    def __init__(self, config: AutomationConfig, github_token: str):
        self.config = config
        self.github_token = github_token
        self.agent: Optional[ChatAgent] = None
        self.is_running = False
        self.reports: List[AutomationReport] = []
        
        # Initialize the scanner
        from document_controller import DocumentScanner, DocumentController
        self.scanner = DocumentScanner()
        self.controller = DocumentController(github_token)
    
    async def initialize_agent(self):
        """Initialize the AI agent for automation"""
        if self.agent:
            return
            
        try:
            openai_client = AsyncOpenAI(
                base_url="https://models.github.ai/inference",
                api_key=self.github_token,
            )
            
            chat_client = OpenAIChatClient(
                async_client=openai_client,
                model_id="openai/gpt-4.1-mini"
            )
            
            self.agent = ChatAgent(
                chat_client=chat_client,
                name="AutomationAgent",
                instructions="""You are an intelligent document automation assistant. Your role is to:
                1. Analyze automation results and provide insights
                2. Generate recommendations for file organization
                3. Identify patterns in file usage and suggest optimizations
                4. Create automated cleanup strategies
                5. Provide clear, actionable automation reports
                
                Always prioritize user safety and never suggest irreversible actions without explicit consent.
                Focus on efficiency, organization, and space optimization."""
            )
            
            logger.info("Automation agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def daily_cleanup(self) -> AutomationReport:
        """Daily automation: Quick cleanup and duplicate detection"""
        logger.info("Starting daily cleanup automation...")
        
        report = AutomationReport(
            timestamp=datetime.now(),
            task_type="daily",
            directories_processed=[],
            files_scanned=0,
            duplicates_found=0,
            duplicates_removed=0,
            files_organized=0,
            files_archived=0,
            space_saved_mb=0.0,
            errors=[],
            recommendations=[]
        )
        
        try:
            for directory in self.config.monitor_directories:
                if not os.path.exists(directory):
                    logger.warning(f"Directory not found: {directory}")
                    continue
                
                logger.info(f"Processing directory: {directory}")
                report.directories_processed.append(directory)
                
                # Quick scan for recent files only (last 7 days)
                documents = self.scanner.scan_directory(directory, max_files=1000)
                recent_docs = [
                    doc for doc in documents 
                    if (datetime.now() - doc.modified_date).days <= 7
                ]
                
                report.files_scanned += len(recent_docs)
                
                # Find duplicates
                duplicates = self._find_duplicates(recent_docs)
                report.duplicates_found += len([d for group in duplicates.values() for d in group]) - len(duplicates)
                
                # Auto-remove small duplicates if enabled
                if self.config.auto_delete_duplicates:
                    removed_count, space_saved = await self._auto_remove_duplicates(duplicates, directory)
                    report.duplicates_removed += removed_count
                    report.space_saved_mb += space_saved
                
                # Quick organization of common file types
                if self.config.auto_organize_files:
                    organized_count = await self._quick_organize(directory, recent_docs)
                    report.files_organized += organized_count
        
        except Exception as e:
            error_msg = f"Daily cleanup error: {e}"
            logger.error(error_msg)
            report.errors.append(error_msg)
        
        # Generate AI recommendations
        if self.agent:
            try:
                recommendations = await self._generate_recommendations(report, "daily")
                report.recommendations = recommendations
            except Exception as e:
                logger.error(f"Failed to generate recommendations: {e}")
        
        self.reports.append(report)
        await self._save_report(report)
        logger.info(f"Daily cleanup completed. Files scanned: {report.files_scanned}")
        
        return report
    
    async def weekly_cleanup(self) -> AutomationReport:
        """Weekly automation: Full organization and old file management"""
        logger.info("Starting weekly cleanup automation...")
        
        report = AutomationReport(
            timestamp=datetime.now(),
            task_type="weekly",
            directories_processed=[],
            files_scanned=0,
            duplicates_found=0,
            duplicates_removed=0,
            files_organized=0,
            files_archived=0,
            space_saved_mb=0.0,
            errors=[],
            recommendations=[]
        )
        
        try:
            for directory in self.config.monitor_directories:
                if not os.path.exists(directory):
                    continue
                
                logger.info(f"Full weekly processing: {directory}")
                report.directories_processed.append(directory)
                
                # Full directory scan
                documents = self.scanner.scan_directory(directory, max_files=10000)
                report.files_scanned += len(documents)
                
                # Comprehensive duplicate detection
                duplicates = self._find_duplicates(documents)
                all_duplicates = sum(len(group) - 1 for group in duplicates.values())
                report.duplicates_found += all_duplicates
                
                # Auto-remove duplicates if enabled
                if self.config.auto_delete_duplicates:
                    removed_count, space_saved = await self._auto_remove_duplicates(duplicates, directory)
                    report.duplicates_removed += removed_count
                    report.space_saved_mb += space_saved
                
                # Full file organization
                if self.config.auto_organize_files:
                    organized_count = await self._full_organize(directory, documents)
                    report.files_organized += organized_count
                
                # Archive old files
                if self.config.auto_archive_old_files:
                    archived_count, archived_space = await self._archive_old_files(directory, documents)
                    report.files_archived += archived_count
                    report.space_saved_mb += archived_space
        
        except Exception as e:
            error_msg = f"Weekly cleanup error: {e}"
            logger.error(error_msg)
            report.errors.append(error_msg)
        
        # Generate AI recommendations
        if self.agent:
            try:
                recommendations = await self._generate_recommendations(report, "weekly")
                report.recommendations = recommendations
            except Exception as e:
                logger.error(f"Failed to generate recommendations: {e}")
        
        self.reports.append(report)
        await self._save_report(report)
        logger.info(f"Weekly cleanup completed. Files processed: {report.files_scanned}")
        
        return report
    
    async def monthly_cleanup(self) -> AutomationReport:
        """Monthly automation: Deep analysis and optimization"""
        logger.info("Starting monthly deep cleanup automation...")
        
        report = AutomationReport(
            timestamp=datetime.now(),
            task_type="monthly",
            directories_processed=[],
            files_scanned=0,
            duplicates_found=0,
            duplicates_removed=0,
            files_organized=0,
            files_archived=0,
            space_saved_mb=0.0,
            errors=[],
            recommendations=[]
        )
        
        try:
            # Deep analysis across all directories
            all_documents = []
            
            for directory in self.config.monitor_directories:
                if not os.path.exists(directory):
                    continue
                
                logger.info(f"Deep monthly processing: {directory}")
                report.directories_processed.append(directory)
                
                # Comprehensive scan including subdirectories
                documents = self.scanner.scan_directory(directory, max_files=50000)
                all_documents.extend(documents)
                report.files_scanned += len(documents)
            
            # Cross-directory duplicate detection
            global_duplicates = self._find_duplicates(all_documents)
            all_duplicates = sum(len(group) - 1 for group in global_duplicates.values())
            report.duplicates_found += all_duplicates
            
            # Storage optimization
            large_files = [doc for doc in all_documents if doc.size > 100 * 1024 * 1024]  # > 100MB
            old_files = [
                doc for doc in all_documents 
                if (datetime.now() - doc.modified_date).days > self.config.old_file_threshold_days
            ]
            
            # Generate comprehensive recommendations
            await self.initialize_agent()
            if self.agent:
                monthly_analysis = {
                    "total_files": len(all_documents),
                    "total_size_gb": sum(doc.size for doc in all_documents) / (1024**3),
                    "duplicates_count": all_duplicates,
                    "large_files_count": len(large_files),
                    "old_files_count": len(old_files),
                    "directories": report.directories_processed
                }
                
                analysis_prompt = f"""
                Analyze this monthly file system report and provide optimization recommendations:
                {json.dumps(monthly_analysis, indent=2)}
                
                Focus on:
                1. Storage optimization strategies
                2. File organization improvements  
                3. Automation rule suggestions
                4. Long-term maintenance plans
                """
                
                result = await self.agent.run(analysis_prompt)
                report.recommendations = [result.text]
        
        except Exception as e:
            error_msg = f"Monthly cleanup error: {e}"
            logger.error(error_msg)
            report.errors.append(error_msg)
        
        self.reports.append(report)
        await self._save_report(report)
        logger.info(f"Monthly analysis completed. Total files analyzed: {report.files_scanned}")
        
        return report
    
    def _find_duplicates(self, documents: List) -> Dict[str, List]:
        """Find duplicate files by hash"""
        hash_groups = {}
        
        for doc in documents:
            if doc.hash_value:
                if doc.hash_value not in hash_groups:
                    hash_groups[doc.hash_value] = []
                hash_groups[doc.hash_value].append(doc)
        
        # Return only groups with duplicates
        return {hash_val: docs for hash_val, docs in hash_groups.items() if len(docs) > 1}
    
    async def _auto_remove_duplicates(self, duplicates: Dict, base_directory: str) -> Tuple[int, float]:
        """Automatically remove duplicate files (keeping the newest)"""
        removed_count = 0
        space_saved = 0.0
        
        for hash_val, docs in duplicates.items():
            if len(docs) <= 1:
                continue
            
            # Sort by modification date (newest first)
            docs.sort(key=lambda x: x.modified_date, reverse=True)
            
            # Keep the first (newest), remove others
            for doc in docs[1:]:
                try:
                    # Only remove if file is larger than threshold
                    if doc.size > self.config.duplicate_size_threshold_mb * 1024 * 1024:
                        os.remove(doc.path)
                        removed_count += 1
                        space_saved += doc.size / (1024 * 1024)  # Convert to MB
                        logger.info(f"Removed duplicate: {doc.name}")
                except Exception as e:
                    logger.error(f"Failed to remove {doc.path}: {e}")
        
        return removed_count, space_saved
    
    async def _quick_organize(self, directory: str, documents: List) -> int:
        """Quick organization of recent files"""
        organized_count = 0
        
        # Define organization structure
        org_folders = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv'],
            'Presentations': ['.ppt', '.pptx']
        }
        
        # Create folders if they don't exist
        for folder_name in org_folders.keys():
            folder_path = os.path.join(directory, folder_name)
            os.makedirs(folder_path, exist_ok=True)
        
        # Move files
        for doc in documents:
            try:
                for folder_name, extensions in org_folders.items():
                    if doc.extension.lower() in extensions:
                        target_dir = os.path.join(directory, folder_name)
                        target_path = os.path.join(target_dir, doc.name)
                        
                        # Avoid conflicts
                        counter = 1
                        while os.path.exists(target_path):
                            name_parts = os.path.splitext(doc.name)
                            target_path = os.path.join(target_dir, f"{name_parts[0]}_{counter}{name_parts[1]}")
                            counter += 1
                        
                        shutil.move(doc.path, target_path)
                        organized_count += 1
                        break
            except Exception as e:
                logger.error(f"Failed to organize {doc.path}: {e}")
        
        return organized_count
    
    async def _full_organize(self, directory: str, documents: List) -> int:
        """Full file organization with date-based structure"""
        organized_count = 0
        
        # Create date-based organization for documents
        for doc in documents:
            try:
                year = doc.modified_date.strftime("%Y")
                month = doc.modified_date.strftime("%m-%B")
                
                # Determine category
                category = self._get_file_category(doc.extension)
                if not category:
                    continue
                
                target_dir = os.path.join(directory, "Organized", category, year, month)
                os.makedirs(target_dir, exist_ok=True)
                
                target_path = os.path.join(target_dir, doc.name)
                
                # Handle conflicts
                counter = 1
                while os.path.exists(target_path):
                    name_parts = os.path.splitext(doc.name)
                    target_path = os.path.join(target_dir, f"{name_parts[0]}_{counter}{name_parts[1]}")
                    counter += 1
                
                shutil.move(doc.path, target_path)
                organized_count += 1
                
            except Exception as e:
                logger.error(f"Failed to organize {doc.path}: {e}")
        
        return organized_count
    
    def _get_file_category(self, extension: str) -> Optional[str]:
        """Get file category based on extension"""
        categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.wma'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c']
        }
        
        for category, extensions in categories.items():
            if extension.lower() in extensions:
                return category
        
        return None
    
    async def _archive_old_files(self, directory: str, documents: List) -> Tuple[int, float]:
        """Archive files older than threshold"""
        archived_count = 0
        archived_space = 0.0
        
        cutoff_date = datetime.now() - timedelta(days=self.config.old_file_threshold_days)
        old_files = [doc for doc in documents if doc.modified_date < cutoff_date]
        
        if not old_files:
            return 0, 0.0
        
        # Create archive directory
        archive_dir = os.path.join(directory, "Archive", datetime.now().strftime("%Y-%m"))
        os.makedirs(archive_dir, exist_ok=True)
        
        for doc in old_files:
            try:
                target_path = os.path.join(archive_dir, doc.name)
                
                # Handle conflicts
                counter = 1
                while os.path.exists(target_path):
                    name_parts = os.path.splitext(doc.name)
                    target_path = os.path.join(archive_dir, f"{name_parts[0]}_{counter}{name_parts[1]}")
                    counter += 1
                
                shutil.move(doc.path, target_path)
                archived_count += 1
                archived_space += doc.size / (1024 * 1024)
                
            except Exception as e:
                logger.error(f"Failed to archive {doc.path}: {e}")
        
        return archived_count, archived_space
    
    async def _generate_recommendations(self, report: AutomationReport, task_type: str) -> List[str]:
        """Generate AI-powered recommendations"""
        try:
            await self.initialize_agent()
            if not self.agent:
                return ["AI recommendations unavailable"]
            
            prompt = f"""
            Analyze this {task_type} automation report and provide 3-5 specific recommendations:
            
            Report Summary:
            - Files scanned: {report.files_scanned}
            - Duplicates found: {report.duplicates_found}
            - Files organized: {report.files_organized}
            - Space saved: {report.space_saved_mb:.2f} MB
            - Errors: {len(report.errors)}
            
            Provide actionable recommendations for improving file management and automation.
            """
            
            result = await self.agent.run(prompt)
            return result.text.split('\n') if result.text else []
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return [f"Recommendation generation failed: {e}"]
    
    async def _save_report(self, report: AutomationReport):
        """Save automation report to file"""
        try:
            reports_dir = "automation_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{report.task_type}_report_{timestamp}.json"
            filepath = os.path.join(reports_dir, filename)
            
            # Convert report to dict for JSON serialization
            report_dict = asdict(report)
            report_dict['timestamp'] = report.timestamp.isoformat()
            
            with open(filepath, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            logger.info(f"Report saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def setup_schedule(self):
        """Setup automation schedules"""
        if self.config.daily_enabled:
            schedule.every().day.at("02:00").do(
                lambda: asyncio.create_task(self.daily_cleanup())
            )
            logger.info("Daily cleanup scheduled for 02:00")
        
        if self.config.weekly_enabled:
            schedule.every().sunday.at("03:00").do(
                lambda: asyncio.create_task(self.weekly_cleanup())
            )
            logger.info("Weekly cleanup scheduled for Sunday 03:00")
        
        if self.config.monthly_enabled:
            schedule.every().month.do(
                lambda: asyncio.create_task(self.monthly_cleanup())
            )
            logger.info("Monthly cleanup scheduled for 1st of each month")
    
    def start_automation(self):
        """Start the automation scheduler"""
        logger.info("Starting automation scheduler...")
        self.is_running = True
        
        self.setup_schedule()
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_automation(self):
        """Stop the automation scheduler"""
        logger.info("Stopping automation scheduler...")
        self.is_running = False


async def main():
    """Main function to run the automation agent"""
    # Load configuration
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: Please set GITHUB_TOKEN environment variable")
        return
    
    # Create configuration
    config = AutomationConfig()
    
    # Override settings from environment if available
    config.daily_enabled = os.getenv("DAILY_AUTOMATION", "true").lower() == "true"
    config.weekly_enabled = os.getenv("WEEKLY_AUTOMATION", "true").lower() == "true"
    config.monthly_enabled = os.getenv("MONTHLY_AUTOMATION", "true").lower() == "true"
    config.auto_delete_duplicates = os.getenv("AUTO_DELETE_DUPLICATES", "false").lower() == "true"
    config.auto_organize_files = os.getenv("AUTO_ORGANIZE_FILES", "true").lower() == "true"
    config.auto_archive_old_files = os.getenv("AUTO_ARCHIVE_OLD_FILES", "false").lower() == "true"
    
    # Initialize scheduler
    scheduler = AutomationScheduler(config, github_token)
    
    print("🤖 AI Document Controller - Automation Agent")
    print("=" * 50)
    print("Automation Settings:")
    print(f"📅 Daily cleanup: {'✅ Enabled' if config.daily_enabled else '❌ Disabled'}")
    print(f"📅 Weekly organization: {'✅ Enabled' if config.weekly_enabled else '❌ Disabled'}")
    print(f"📅 Monthly deep analysis: {'✅ Enabled' if config.monthly_enabled else '❌ Disabled'}")
    print(f"🗑️ Auto-delete duplicates: {'✅ Enabled' if config.auto_delete_duplicates else '❌ Disabled'}")
    print(f"📁 Auto-organize files: {'✅ Enabled' if config.auto_organize_files else '❌ Disabled'}")
    print(f"📦 Auto-archive old files: {'✅ Enabled' if config.auto_archive_old_files else '❌ Disabled'}")
    print("\nMonitored Directories:")
    for directory in config.monitor_directories:
        print(f"  📂 {directory}")
    
    print("\n🚀 Starting automation scheduler...")
    print("Press Ctrl+C to stop")
    
    try:
        # Test run
        choice = input("\nWould you like to do a test run first? (y/n): ").lower()
        if choice == 'y':
            print("\n🧪 Running test automation...")
            
            await scheduler.initialize_agent()
            
            test_choice = input("Choose test: (1) Daily, (2) Weekly, (3) Monthly: ")
            if test_choice == "1":
                report = await scheduler.daily_cleanup()
            elif test_choice == "2":
                report = await scheduler.weekly_cleanup()
            elif test_choice == "3":
                report = await scheduler.monthly_cleanup()
            else:
                print("Invalid choice")
                return
            
            print(f"\n📊 Test Results:")
            print(f"Files scanned: {report.files_scanned}")
            print(f"Duplicates found: {report.duplicates_found}")
            print(f"Files organized: {report.files_organized}")
            print(f"Space saved: {report.space_saved_mb:.2f} MB")
            print(f"Errors: {len(report.errors)}")
            
            if report.recommendations:
                print("\n💡 AI Recommendations:")
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"{i}. {rec}")
            
            start_scheduler = input("\nStart continuous automation? (y/n): ").lower()
            if start_scheduler != 'y':
                return
        
        # Start continuous automation
        scheduler.start_automation()
        
    except KeyboardInterrupt:
        print("\n👋 Stopping automation...")
        scheduler.stop_automation()


if __name__ == "__main__":
    asyncio.run(main())