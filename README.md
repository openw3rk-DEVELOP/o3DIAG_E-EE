<h2>
    o3DIAG ELM/ECU Emulator (o3DIAG E/EE) for o3DIAG
</h2>
<p>
  o3DIAG E/EE is a software tool designed to simulate a vehicle's OBD-II interface. 
  It opens a virtual COM port and communicates with OBD-II software or tools as if it were a real ECU.
</p>
<p>
    The emulator can respond to standard OBD-II commands such as reading Diagnostic Trouble Codes (DTCs), vehicle VIN, and live engine data like RPM and speed.
</p>
<p>
    It supports basic ELM327 AT commands to control echo, linefeeds, headers, and protocol settings.
</p>
<p>
    The program formats responses in the same way a real ECU would, allowing connected tools to read realistic error codes and vehicle information.
</p>
<p>
    The COM port and baud rate can be configured within the program to match the virtual or physical serial interface being used.
</p>
<p>
    Overall, it provides a safe environment for testing OBD-II software without requiring a real vehicle.
</p>
<p>
    <br>
    <h4>NOTE:</h4>
    <strong>The o3DIAG ELM/ECU Emulator requires a virtual COM-PORT over a COM-PAIR.</strong><br><br>
    <strong>Please adjust the script in the config area before running it, note the correct COM-PORT and the baud rate</strong>
</p>
<br>
<h4>Information for developers</h4>
o3DIAG Source on GitHub: <a href="https://github.com/openw3rk-DEVELOP/o3DIAG">https://github.com/openw3rk-DEVELOP/o3DIAG</a>
<p><strong>
o3DIAG E/EE is open source and licensed under MIT-LICENSE.<br>
Copyright (c) openw3rk INVENT</p>
