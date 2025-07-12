# Code Restructuring Plan (No New Code)

## Current Structure Analysis

### Root Level Files (Too Many)

- `pc_receiver.py` (24KB, 665 lines) - Main application
- `pynq_receiver.py` (8.3KB, 250 lines) - Hardware interface
- `controller.py` (1.5KB, 80 lines) - Simple GUI (redundant)
- `dutycycle.py` (1.7KB, 83 lines) - PWM control
- `pwm_test_notebook.py` (1.7KB, 83 lines) - Duplicate of dutycycle.py
- `temp.py` (1.1KB, 36 lines) - Temperature plotting
- `practice_pynq_notebook.py` (1.1KB, 45 lines) - Learning/example code
- `solenoidTest.py` - Missing file (referenced but not found)

### Configuration Files

- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies (conflicting)
- `package-lock.json` - Node.js lock file
- `Brewfile` - macOS dependencies

### Data Files

- `names.db` - SQLite database
- `commands.db` - Empty SQLite database

### Documentation

- `README.md` - Basic project info

## Recommended Restructuring

### 1. Create Logical Directories

```
ATOMCRAFT---instrumentation-and-Controls/
├── README.md
├── requirements.txt
├── Brewfile
├── .gitignore
├── main/                          # Core application files
│   ├── pc_receiver.py            # Main PC application
│   ├── pynq_receiver.py          # PYNQ hardware interface
│   └── controller.py             # Simple controller (if needed)
├── hardware/                      # Hardware control modules
│   ├── dutycycle.py              # PWM control (keep this one)
│   └── temp.py                   # Temperature monitoring
├── examples/                      # Learning and test files
│   ├── pwm_test_notebook.py      # PWM testing
│   └── practice_pynq_notebook.py # Learning examples
├── data/                         # Database and data files
│   ├── names.db
│   └── commands.db
├── docs/                         # Documentation
│   └── README.md                 # Move current README here
└── config/                       # Configuration files
    ├── package.json              # Move Node.js config here
    └── package-lock.json         # Move Node.js lock here
```

### 2. File Consolidation Strategy

#### Keep These Files (Core Functionality):

- `pc_receiver.py` → `main/pc_receiver.py`
- `pynq_receiver.py` → `main/pynq_receiver.py`
- `dutycycle.py` → `hardware/dutycycle.py`
- `temp.py` → `hardware/temp.py`

#### Move These Files (Examples/Testing):

- `pwm_test_notebook.py` → `examples/pwm_test_notebook.py`
- `practice_pynq_notebook.py` → `examples/practice_pynq_notebook.py`

#### Evaluate These Files:

- `controller.py` → Consider if it's needed or if `pc_receiver.py` covers this functionality
- `solenoidTest.py` → Find and move to `examples/` if it exists

#### Organize Configuration:

- `package.json` → `config/package.json`
- `package-lock.json` → `config/package-lock.json`
- `names.db` → `data/names.db`
- `commands.db` → `data/commands.db`

### 3. Benefits of This Restructure

1. **Clear Separation**: Core app vs examples vs hardware modules
2. **Reduced Root Clutter**: Only essential files at root level
3. **Logical Grouping**: Related files are together
4. **Easier Navigation**: Developers know where to find things
5. **No Code Changes**: Just moving existing files around

### 4. Implementation Steps

1. Create the new directory structure
2. Move files to their new locations
3. Update any import statements that reference moved files
4. Update documentation to reflect new structure
5. Test that everything still works

### 5. Files to Consider Removing

- `get-pip.py` (2.2MB) - This is a one-time installer, not needed in repo
- `.DS_Store` - macOS system file, should be in .gitignore
- `node_modules/` - Should be in .gitignore, not committed

### 6. Import Statement Updates Needed

After moving files, you'll need to update:

- Any relative imports in the Python files
- Any hardcoded paths to database files
- Any references to moved configuration files

This restructuring will make the codebase much more organized and maintainable without changing any actual code logic.
