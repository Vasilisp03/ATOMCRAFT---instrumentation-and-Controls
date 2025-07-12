# AtomCraft Instrumentation and Controls

See docs/README.md for detailed information.

## Quick Start

### Prerequisites

- Python 3.12+
- Homebrew (for macOS)

### Setup

1. Install Tkinter support:

   ```bash
   brew install python-tk
   ```

2. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

You have several options to run the PC receiver:

**Option 1: Using the shell script**

```bash
./run_pc_receiver.sh
```

**Option 2: Using the Python script**

```bash
./run_pc_receiver.py
```

**Option 3: Manual activation**

```bash
source .venv/bin/activate
python main/pc_receiver.py
```

### Troubleshooting

If you encounter the `ModuleNotFoundError: No module named '_tkinter'` error:

1. Make sure you're using the virtual environment (`.venv`)
2. Ensure `python-tk` is installed via Homebrew
3. Use one of the provided run scripts above

## Project Structure

- `main/` - Core application files
- `hardware/` - Hardware interface modules
- `examples/` - Example scripts and notebooks
- `Control/` - Control system prototypes
- `docs/` - Documentation
