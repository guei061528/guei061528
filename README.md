# guei061528

- 👋 Hi, I'm Xiao Guei
- 👀 I'm interested in coding, stock, and fitness.
- 🌱 I'm currently learning ...
- 💞️ I'm looking to collaborate on ...
- 📫 How to reach me ...

## JIRA Auto-Creation System with Degrade Mechanism

This repository contains an automated JIRA creation system with intelligent degrade detection for test failures.

### Features

- **Automatic JIRA Creation**: Creates JIRA sub-tasks from JSON test information
- **Degrade Detection**: Intelligently detects when tests go from PASS to FAIL
- **Smart Commenting**: Adds comments to existing JIRA issues for repeated failures with same error
- **History Tracking**: Maintains test result history across versions

### Quick Start

See [DEGRADE_README.md](DEGRADE_README.md) for detailed documentation.

```bash
# Run the demo
python demo_degrade.py

# Run tests
python -m unittest test_degrade.py

# Create JIRA from test results
python jira_create.py --project MA --parent MA-1234 --json examples/test_fail_v808.json
```

### Files

- `jira_create.py` - Main JIRA creation script with degrade support
- `degrade_tracker.py` - Degrade detection and history tracking
- `JIRABase.py` - JIRA API interface (stub)
- `test_degrade.py` - Comprehensive test suite
- `demo_degrade.py` - Interactive demonstration
- `DEGRADE_README.md` - Detailed documentation
- `examples/` - Sample test result JSON files
