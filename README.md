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
   
## Using
-  Model your system using [PIPE2](https://sourceforge.net/projects/pipe2/)
-  For timed transitions, place the timer value (in seconds) at the 'rate' property
- Name your places as P<span style="color:red">xxxx</span> or P<span style="color:red">xxxx</span> (<span style="color:blue">list of digital outputs, using semicolons (\;) as delimiters</span>) 
   - valid digital outputs are DO0,DO1, ..., DO15

- Name your transitions as T<span style="color:red">xxxx</span> or T<span style="color:red">xxxx</span> (<span style="color:blue">boolean expression</span>) 
   -  valid digital inputs to be used on boolean expression are DI0, DI1, ..., DI7

   - Besides digital inputs, one can use the literals 'true' and 'false', parenthesis, and boolean operators
   - Boolean operators are 
      - AND: 'and', '&&'
      - OR:  'or', '||'
      - XOR: 'xor', '^'
      - NOT: 'not', '!', '~'
 
 When in doubt, please refer to the [example files](https://github.com/henrique-santos-silva/petrinet_plc/tree/main/Demo%20Petri%20Nets/xml) provided to see how the XML should be structured
 