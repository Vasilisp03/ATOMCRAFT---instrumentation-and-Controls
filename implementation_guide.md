# Implementation Guide: Restructuring Existing Codebase

## Step-by-Step Instructions

### Step 1: Create New Directory Structure

Run these commands in your terminal from the project root:

```bash
# Create main directories
mkdir -p main
mkdir -p hardware
mkdir -p examples
mkdir -p data
mkdir -p docs
mkdir -p config

# Create __init__.py files for Python packages
touch main/__init__.py
touch hardware/__init__.py
touch examples/__init__.py
```

### Step 2: Move Core Application Files

```bash
# Move main application files
mv pc_receiver.py main/
mv pynq_receiver.py main/
mv controller.py main/
```

### Step 3: Move Hardware Control Files

```bash
# Move hardware control files
mv dutycycle.py hardware/
mv temp.py hardware/
```

### Step 4: Move Example and Test Files

```bash
# Move example and test files
mv pwm_test_notebook.py examples/
mv practice_pynq_notebook.py examples/
```

### Step 5: Move Data Files

```bash
# Move database files
mv names.db data/
mv commands.db data/
```

### Step 6: Move Configuration Files

```bash
# Move Node.js configuration files
mv package.json config/
mv package-lock.json config/
```

### Step 7: Move Documentation

```bash
# Move and rename README
mv README.md docs/README.md
# Create a new simple README at root
echo "# AtomCraft Instrumentation and Controls" > README.md
echo "See docs/README.md for detailed information." >> README.md
```

### Step 8: Update Database Paths

After moving the files, you'll need to update the database paths in these files:

**Files to update:**

- `main/pc_receiver.py` (6 instances)
- `main/controller.py` (4 instances)

**Change from:**

```python
conn = sqlite3.connect("names.db")
```

**Change to:**

```python
conn = sqlite3.connect("data/names.db")
```

### Step 9: Update .gitignore

Add these entries to your `.gitignore` file:

```gitignore
# System files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/

# Node.js
node_modules/

# IDE
.vscode/
.idea/

# Data files (if you want to ignore them)
# data/*.db
```

### Step 10: Clean Up Unnecessary Files

Consider removing these files:

```bash
# Remove large installer file (not needed in repo)
rm get-pip.py

# Remove system files
rm .DS_Store

# Remove node_modules (should be in .gitignore)
rm -rf node_modules/
```

### Step 11: Test the Restructured Code

After moving files, test that everything still works:

```bash
# Test main application
cd main
python pc_receiver.py

# Test hardware modules
cd ../hardware
python dutycycle.py

# Test examples
cd ../examples
python pwm_test_notebook.py
```

## Final Directory Structure

After restructuring, your project should look like this:

```
ATOMCRAFT---instrumentation-and-Controls/
├── README.md                    # Simple root README
├── requirements.txt             # Python dependencies
├── Brewfile                     # macOS dependencies
├── .gitignore                   # Git ignore rules
├── main/                        # Core application files
│   ├── __init__.py
│   ├── pc_receiver.py          # Main PC application
│   ├── pynq_receiver.py        # PYNQ hardware interface
│   └── controller.py           # Simple controller
├── hardware/                    # Hardware control modules
│   ├── __init__.py
│   ├── dutycycle.py            # PWM control
│   └── temp.py                 # Temperature monitoring
├── examples/                    # Learning and test files
│   ├── __init__.py
│   ├── pwm_test_notebook.py    # PWM testing
│   └── practice_pynq_notebook.py # Learning examples
├── data/                       # Database and data files
│   ├── names.db
│   └── commands.db
├── docs/                       # Documentation
│   └── README.md              # Detailed project documentation
├── config/                     # Configuration files
│   ├── package.json           # Node.js dependencies
│   └── package-lock.json      # Node.js lock file
└── Control/                    # Existing Control directory (unchanged)
    └── Prototypes/
        ├── TF_Coil_PID.ino
        ├── TF_Coil_test.py
        └── hall_sensor_notebook.py
```

## Benefits Achieved

1. **Cleaner Root Directory**: Only essential files at the top level
2. **Logical Organization**: Related files are grouped together
3. **Easier Navigation**: Clear structure for new developers
4. **Better Maintainability**: Separated concerns and examples
5. **No Code Changes**: All existing functionality preserved

## Notes

- The `Control/` directory was left unchanged as it seems to be a separate component
- All import statements use standard library modules, so no import path updates needed
- Only database file paths need to be updated
- The restructuring maintains all existing functionality
