# petrinet_plc
Petri net-based Programmable Logic Controller



## Setup

### Linux

1. **Remove Existing Virtual Environment (if any):**

   ```bash
   # Navigate to your project directory (if not already there)
   cd /path/to/petrinet_plc
   
   # Remove existing virtual environment (if it exists)
   if [ -d "venv" ]; then
       rm -r venv
   fi
2. **Create a new virtual environment:**
   ```bash
   python3 -m venv venv
3. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate
4. **Install Project Dependencies:**
   ```bash
   pip install -r requirements_linux.txt
### Windows
1. **Remove Existing Virtual Environment (if any):**
    ```   
    :: Navigate to your project directory (if not already there)
    cd C:\path\to\petrinet_plc
    :: Remove existing virtual environment (if it exists)
    if exist venv rmdir /s /q venv
2. **Create a new virtual environment:**
   ```
    python -m venv venv
3. **Activate the Virtual Environment:**
   ```
    venv\Scripts\activate
4. **Install Project Dependencies:**
   ```
   pip install -r requirements_windows.txt

## Running
1. **run the run.py script**
   ```bash
   python run.py
2. **Open browser**
   * **Human Machine Interface**:[http://[::1]:50000](http://[::1]:50000)
   * **IOs Emulator**[http://[::1]:50001](http://[::1]:50001)
   * **PetriNet live view**[http://[::1]:50000/debug](http://[::1]:50000/debug)
   
