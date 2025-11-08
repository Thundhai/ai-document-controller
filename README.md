# 🤖 AI Document Controller Agent

An intelligent document management agent that helps you organize, clean up, and manage documents on your laptop using AI. The agent now includes **automation capabilities** for daily, weekly, and monthly document management tasks.

## ✨ Features

- **🔍 Smart Document Scanning**: Recursively scan directories and analyze document metadata
- **🔄 Duplicate Detection**: Find exact duplicate files using content hashing
- **📊 Disk Usage Analysis**: Analyze space usage by file type and size
- **📅 Old File Detection**: Identify files that haven't been modified in a specified time period
- **💡 Organization Suggestions**: Get AI-powered recommendations for document organization
- **🤖 Interactive Chat Interface**: Natural language interaction with the AI agent
- **⚡ CLI Support**: Command-line interface for quick scans and batch operations
- **🔄 AUTOMATION**: Daily, weekly, and monthly automated cleanup tasks
- **📅 Task Scheduling**: Windows Task Scheduler integration for hands-free operation
- **📊 Automation Reports**: Detailed reports with AI-powered recommendations

## 🆕 Automation Features

### 📅 **Daily Automation** (2:00 AM)
- Quick scan of recent files (last 7 days)
- Duplicate detection and optional auto-removal
- Basic file organization
- Quick cleanup reports

### 📅 **Weekly Automation** (Sunday 3:00 AM)
- Full directory scan and organization
- Comprehensive duplicate management
- File type categorization with date-based structure
- Old file archival (optional)

### 📅 **Monthly Automation** (1st of month 4:00 AM)
- Deep cross-directory analysis
- Storage optimization recommendations
- Long-term file management strategies
- Comprehensive AI-powered insights

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **GitHub Personal Access Token** for accessing GitHub Models
   - Get one from: https://github.com/settings/tokens
   - No special permissions needed for public access

### Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd document-controller
   ```

2. **Set up your environment**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your GitHub token
   # GITHUB_TOKEN=your_github_token_here
   ```

3. **Install dependencies** (The `--pre` flag is required for Microsoft Agent Framework)
   ```bash
   pip install agent-framework-azure-ai --pre
   pip install openai>=1.0.0 python-dotenv>=1.0.0 schedule>=1.2.0
   ```

### Usage

#### 🤖 **Automation Mode (NEW!)**

**Set up automated scheduling:**
```bash
# Run as Administrator
PowerShell -ExecutionPolicy Bypass -File setup_automation.ps1
```

**Manual automation runs:**
```bash
# Test daily cleanup
python automation_launcher.py daily

# Test weekly organization  
python automation_launcher.py weekly

# Test monthly deep analysis
python automation_launcher.py monthly

# Start continuous scheduler
python automation_launcher.py schedule
```

#### 🗣️ **Interactive Mode**

Run the AI agent in interactive mode for natural language conversations:

```bash
python document_controller.py
```

Or use the CLI wrapper:

```bash
python cli.py --mode interactive
```

#### ⚡ **Quick Scan Mode**

Perform a quick analysis of a directory:

```bash
# Scan your Downloads folder
python cli.py --mode scan --directory "C:\Users\YourName\Downloads"

# Scan your Documents folder
python cli.py --mode scan --directory "C:\Users\YourName\Documents"
```

#### 🎮 **Using VS Code Tasks**

If you're using VS Code, you can use the predefined tasks:
- **Ctrl+Shift+P** → **Tasks: Run Task** → Choose from:
  - "Run Document Controller (Interactive)"
  - "🤖 Run Daily Automation"
  - "📅 Run Weekly Automation"  
  - "📊 Run Monthly Automation"
  - "⚙️ Start Automation Scheduler"
  - "🛠️ Setup Windows Task Scheduler"

## ⚙️ **Automation Configuration**

### Environment Variables

Configure automation in your `.env` file:

```env
# Automation Schedule Settings
DAILY_AUTOMATION=true
WEEKLY_AUTOMATION=true  
MONTHLY_AUTOMATION=true

# Automation Behavior
AUTO_DELETE_DUPLICATES=false  # Set to true to automatically delete duplicates
AUTO_ORGANIZE_FILES=true      # Automatically organize files into folders
AUTO_ARCHIVE_OLD_FILES=false  # Set to true to automatically archive old files

# Thresholds
OLD_FILE_THRESHOLD_DAYS=365   # Files older than this will be considered for archival
DUPLICATE_SIZE_THRESHOLD_MB=1 # Only process duplicates larger than this size

# Safety Settings
DRY_RUN_MODE=false           # Set to true to simulate actions without making changes
BACKUP_BEFORE_DELETE=true   # Create backup before deleting files
MAX_FILES_PER_RUN=10000     # Maximum files to process in one run
```

### 🔒 Safety Features

- **Conservative defaults**: Auto-deletion is disabled by default
- **Size thresholds**: Only processes duplicates above specified size
- **Backup creation**: Optional backup before any deletion
- **Dry run mode**: Test automation without making changes
- **Error logging**: Comprehensive error tracking and reporting
- **User consent**: Clear configuration options for all automated actions

## 🎯 What the Agent Can Do

### 1. **Automated Document Management**
- **Daily**: "The agent runs daily cleanup automatically"
- **Weekly**: "Full organization happens every Sunday"
- **Monthly**: "Deep analysis and optimization monthly"

### 2. **Manual Document Scanning**
Ask the agent to scan any directory:
```
"Please scan my Documents folder"
"Analyze the files in C:\Users\MyName\Downloads"
```

### 3. **Find Duplicates**
Identify duplicate files to save disk space:
```
"Find duplicate files in the last scan"
"Show me which files I can safely delete"
```

### 4. **Analyze Disk Usage**
Understand what's taking up space:
```
"What file types are using the most space?"
"Show me disk usage breakdown"
```

### 5. **Find Old Files**
Identify files for archival or deletion:
```
"Show me files older than 1 year"
"Find files I haven't touched in 2 years"
```

### 6. **Organization Suggestions**
Get AI-powered recommendations:
```
"How should I organize these files?"
"Give me suggestions for cleaning up my documents"
```

## 📁 Project Structure

```
document-controller/
├── document_controller.py      # Main agent implementation
├── automation_agent.py         # NEW: Automation engine
├── automation_launcher.py      # NEW: Simple automation interface
├── cli.py                      # Command-line interface
├── setup_automation.ps1        # NEW: Windows Task Scheduler setup
├── requirements.txt            # Python dependencies
├── .env                        # Configuration (with automation settings)
├── automation_reports/         # NEW: Generated automation reports
├── .vscode/
│   └── tasks.json             # VS Code tasks (with automation)
├── .github/
│   └── copilot-instructions.md # GitHub Copilot instructions
└── README.md                  # This file
```

## 📊 **Automation Reports**

The agent generates detailed reports for each automation run:

- **📈 Performance metrics**: Files processed, space saved, errors
- **🔍 Analysis results**: Duplicates found, organization statistics  
- **💡 AI recommendations**: Intelligent suggestions for improvement
- **📝 JSON format**: Easily parseable automation history
- **📁 Organized storage**: Reports saved in `automation_reports/` directory

Example report:
```json
{
  "timestamp": "2025-11-08T02:00:00",
  "task_type": "daily",
  "files_scanned": 1247,
  "duplicates_found": 23,
  "files_organized": 156,
  "space_saved_mb": 45.6,
  "recommendations": [
    "Consider archiving files older than 2 years",
    "Enable auto-deletion for duplicates smaller than 5MB"
  ]
}
```

## 🔧 Advanced Automation Usage

### Custom Schedules

Modify the automation agent to run at custom intervals:

```python
from automation_agent import AutomationScheduler, AutomationConfig

# Create custom config
config = AutomationConfig()
config.monitor_directories = ["/path/to/custom/dir"]
config.auto_delete_duplicates = True
config.old_file_threshold_days = 180

# Run specific automation
scheduler = AutomationScheduler(config, github_token)
report = await scheduler.daily_cleanup()
```

### Batch Processing
```bash
# Run all automation tasks
python automation_launcher.py daily
python automation_launcher.py weekly  
python automation_launcher.py monthly
```

### Integration with Other Tools
The automation agent can be integrated with:
- **Windows Task Scheduler** (included setup script)
- **PowerShell scripts** for advanced workflows
- **Other Python applications** via the automation classes
- **CI/CD pipelines** for automated document management

## 🔒 Security & Privacy

- **Local Processing**: All document scanning happens locally on your machine
- **AI Analysis**: Only metadata and summaries are sent to the AI model for analysis
- **No File Content Sharing**: The agent doesn't upload your actual file contents
- **Safe Automation**: Conservative defaults prevent accidental data loss
- **Audit Trail**: Comprehensive logging of all automation actions
- **GitHub Token**: Only used to access GitHub Models API, no repository access needed

## 🧪 Example Automation Interactions

### Daily Automation
```
🤖 AI Document Controller - Daily Automation
📅 Running daily cleanup...
📊 Results:
   📁 3 directories processed
   📄 1,247 files scanned  
   🔄 23 duplicates found
   📂 156 files organized
   💾 45.6 MB space saved

💡 AI Recommendations:
1. Enable auto-deletion for small duplicates (<5MB)
2. Consider weekly archive of files >1 year old
3. Downloads folder has 67% unorganized files
```

### Weekly Automation
```
📅 Weekly Organization Complete!
📊 Full scan results:
   📁 3 directories processed
   📄 12,450 files analyzed
   🔄 89 duplicate groups found
   📂 1,234 files organized into date folders
   📦 45 old files archived
   💾 234.7 MB total space optimized

🎯 This week's achievements:
✅ Organized 1,200+ files by date and type
✅ Cleaned up Downloads folder completely  
✅ Archived old project files to safe storage
✅ Identified top space-wasting file types
```

## 🐛 Troubleshooting

### Common Issues

1. **"GitHub token is required" error**
   - Make sure you've set the `GITHUB_TOKEN` environment variable
   - Verify your token is valid at https://github.com/settings/tokens

2. **Automation not running**
   - Check Windows Task Scheduler for created tasks
   - Verify Python path in scheduled tasks
   - Check `automation_agent.log` for errors

3. **"Permission denied" errors during automation**
   - Run setup script as administrator
   - Ensure antivirus isn't blocking file operations
   - Check file permissions on target directories

4. **Files not being organized**
   - Check `AUTO_ORGANIZE_FILES=true` in `.env`
   - Verify target directories exist and are writable
   - Review automation reports for specific errors

### Performance Tips

- Start with conservative settings and gradually enable more automation
- Use `DRY_RUN_MODE=true` to test automation without making changes
- Monitor automation reports to optimize settings
- Adjust `MAX_FILES_PER_RUN` for performance vs. completeness balance

## 📝 Logging

The automation agent creates detailed logs:
- `automation_agent.log`: Automation operations and errors
- `document_controller.log`: Interactive agent activities
- `automation_reports/`: JSON reports for each automation run

## 🤝 Contributing

This AI-generated project demonstrates advanced document management automation. Feel free to:
- Add new automation features
- Improve the scheduling algorithms  
- Add support for cloud storage integration
- Enhance the AI analysis capabilities
- Create custom automation workflows

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with GitHub's terms of service when using GitHub Models.

---

**Happy organizing! 🗂️✨** 
*Your documents will now manage themselves!* 🤖

## 🎯 What the Agent Can Do

### 1. Document Scanning
Ask the agent to scan any directory:
```
"Please scan my Documents folder"
"Analyze the files in C:\Users\MyName\Downloads"
```

### 2. Find Duplicates
Identify duplicate files to save disk space:
```
"Find duplicate files in the last scan"
"Show me which files I can safely delete"
```

### 3. Analyze Disk Usage
Understand what's taking up space:
```
"What file types are using the most space?"
"Show me disk usage breakdown"
```

### 4. Find Old Files
Identify files for archival or deletion:
```
"Show me files older than 1 year"
"Find files I haven't touched in 2 years"
```

### 5. Organization Suggestions
Get AI-powered recommendations:
```
"How should I organize these files?"
"Give me suggestions for cleaning up my documents"
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Model configuration (optional)
MODEL_ID=openai/gpt-4.1-mini

# Scanning limits (optional)
MAX_FILES_PER_SCAN=10000

# Directories to exclude (optional)
EXCLUDED_DIRECTORIES=.git,.svn,__pycache__,node_modules,.vscode,AppData,System32,Windows
```

### Supported Models

The agent supports various GitHub Models. Popular choices:

- **openai/gpt-4.1-mini** (default) - Good balance of performance and cost
- **openai/gpt-4.1** - Higher quality responses
- **openai/gpt-4o-mini** - Faster, more cost-effective
- **microsoft/phi-4-mini-instruct** - Lightweight option

## 📁 Project Structure

```
document-controller/
├── document_controller.py    # Main agent implementation
├── cli.py                   # Command-line interface
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration template
├── .vscode/
│   └── tasks.json          # VS Code tasks
├── .github/
│   └── copilot-instructions.md  # GitHub Copilot instructions
└── README.md               # This file
```

## 🔒 Security & Privacy

- **Local Processing**: All document scanning happens locally on your machine
- **AI Analysis**: Only metadata and summaries are sent to the AI model for analysis
- **No File Content Sharing**: The agent doesn't upload your actual file contents
- **GitHub Token**: Only used to access GitHub Models API, no repository access needed

## 🧪 Example Interactions

### Basic Scanning
```
You: Scan my Downloads folder
Agent: I'll scan your Downloads folder for documents. Let me analyze what's there...

[Scanning results with file counts, sizes, and types]

I found 247 files totaling 1.2 GB. Would you like me to look for duplicates or analyze specific file types?
```

### Duplicate Detection
```
You: Find duplicate files
Agent: I found 15 groups of duplicate files that could free up 234 MB of space. 
The largest duplicates are:
- vacation_photos.zip (45 MB) - 3 copies
- presentation.pptx (12 MB) - 2 copies

Would you like me to show you the exact locations so you can safely delete the extras?
```

### Organization Help
```
You: How should I organize my documents?
Agent: Based on your file analysis, I recommend:

1. Create folders by type: Documents/, Images/, Archives/
2. Use date-based subfolders for photos (2024/01/, 2024/02/)
3. Move 45 old files (>2 years) to an Archive/ folder
4. Clean up 8 duplicate files to save 156 MB

Would you like specific instructions for any of these steps?
```

## 🔧 Advanced Usage

### Custom Scanning
```python
from document_controller import DocumentController

# Initialize with custom settings
controller = DocumentController(
    github_token="your_token",
    model_id="openai/gpt-4.1"
)

# Scan with custom parameters
documents = controller.scanner.scan_directory("/path/to/scan", max_files=5000)
```

### Batch Processing
```bash
# Scan multiple directories
for dir in Documents Downloads Desktop; do
    python cli.py --mode scan --directory "$HOME/$dir"
done
```

## 🐛 Troubleshooting

### Common Issues

1. **"GitHub token is required" error**
   - Make sure you've set the `GITHUB_TOKEN` environment variable
   - Verify your token is valid at https://github.com/settings/tokens

2. **"Permission denied" errors during scanning**
   - Run as administrator on Windows for system directories
   - Skip problematic directories or adjust excluded directories list

3. **"Module not found" errors**
   - Make sure you installed with `--pre` flag: `pip install agent-framework-azure-ai --pre`
   - Verify all dependencies are installed: `pip install -r requirements.txt`

4. **Slow scanning on large directories**
   - Reduce `MAX_FILES_PER_SCAN` in configuration
   - Add more directories to the exclusion list

### Performance Tips

- Start with smaller directories (Downloads, Desktop) before scanning large drives
- Use the exclusion list to skip unnecessary directories like system files
- The agent processes up to 10,000 files by default - adjust as needed

## 📝 Logging

The agent creates detailed logs in `document_controller.log` including:
- Scan progress and statistics
- Error messages and warnings
- AI agent interactions

## 🤝 Contributing

This is an AI-generated project designed to demonstrate intelligent document management. Feel free to:
- Add new analysis features
- Improve the scanning algorithm
- Add support for more file types
- Enhance the AI prompts

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with GitHub's terms of service when using GitHub Models.

---

**Happy organizing! 🗂️✨**