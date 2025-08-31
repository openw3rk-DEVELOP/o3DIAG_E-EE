# **************************************************************
# * o3DIAG ELM/ECU EMULATOR version 3.5 for o3DIAG             *
# * Copyright (c) openw3rk INVENT                              *
# * https://openw3rk.de | https://o3diag.openw3rk.de           *
# * Licensed under MIT-LICENSE                                 *
# **************************************************************
# * INFO: Please use the config options.                       *
# * NOTE: o3DIAG ELM/ECU EMULATOR requires a virtual COM-PORT. *
# **************************************************************

import serial
import time
import sys
import math
from typing import List

# EMULATOR CONFIG:
# ----------------
PORT = "COM4"   # EMULATOR COM
BAUD = 9600     # BAUD (EMULATE) ADAPTER

# DUMMY-DATA CONFIG:
# ------------------

# VIN:
# ----
VIN = "1C3AB4CD5EF123456" 

# DTCs:
# -----
DTC_CODES = ["00301", "00420", "00149", "00019", "00127", "00087", "00045"]  

# DESCRIPTION OF DTC-CODES:
# -------------------------
# 1. P0301 Zyl.1-Misfire 
# 2. P0420 Bank 1 Catalytic Converter - Efficiency Below Threshold
# 3. P0149 Incorrect Injection Timing
# 4. P0019 Crankshaft Position/Camshaft Position, Bank 2 Sensor B - Reference Failure
# 5. P0127 Intake air temperature too high
# 6. P0087 Fuel Rail/System Pressure Too Low
# 7. P0045 Turbocharger Compressor Control Solenoid - Open Circuit

# LIVE DATA ENGINE:
# -----------------
ENGINE_RPM_BASE = 820 # RPM
VEHICLE_SPEED = 21 # SPEED  

# -----------------------------------------------------------------------------------

class o3DIAG_ELM_ECU_EMU:
    def __init__(self):
        self.echo = True     
        self.linefeeds = False  
        self.headers = False    
        self.spaces = True      
        self.protocol = 0       
        self.voltage = 12.3

    def fmt_line(self, hexstr: str) -> bytes:
        s = hexstr.replace(" ", "").upper()
        bytes_pairs = [s[i:i+2] for i in range(0, len(s), 2)] if s else []
        if self.spaces:
            out = " ".join(bytes_pairs)
        else:
            out = "".join(bytes_pairs)

        eol = "\r\n" if self.linefeeds else "\r"
        return (out + eol + ">").encode("ascii")

    def fmt_textline(self, text: str) -> bytes:
        eol = "\r\n" if self.linefeeds else "\r"
        return (text + eol + ">").encode("ascii")

def strip_cmd(s: str) -> str:
    return "".join(ch for ch in s if ch not in "\r\n ").upper()


def encode_dtc_two_bytes(dtc: str) -> str:
    types = {"P":0b00, "C":0b01, "B":0b10, "U":0b11}
    t = types.get(dtc[0], 0b00)
    d1, d2, d3, d4 = (int(dtc[1]), int(dtc[2]), int(dtc[3]), int(dtc[4]))
    byte1 = (t << 6) | (d1 << 4) | d2
    byte2 = (d3 << 4) | d4
    return f"{byte1:02X}{byte2:02X}"

def build_mode03_response(dtcs: List[str]) -> str:
    payload = "43"
    for code in dtcs:
        payload += encode_dtc_two_bytes(code)
    return payload

def build_mode09_vin_frames(vin: str) -> List[str]:

# 49 02 01 <7 bytes>
# 49 02 02 <7 bytes>
# 49 02 03 <Rest>

    raw = vin.encode("ascii")
    raw = raw[:17].ljust(17, b' ')
    chunks = [raw[i:i+7] for i in range(0, len(raw), 7)]
    frames = []
    for idx, ch in enumerate(chunks, start=1):
        frames.append("4902" + f"{idx:02X}" + "".join(f"{b:02X}" for b in ch))
    return frames

def build_mode01(pid: str, dtc_count: int) -> str:
# - 010C: RPM
# - 010D: Speed

    if pid == "00":
        return "4100 BE 1F A8 13"
    elif pid == "01":
        A = 0x80 | (dtc_count & 0x7F) if dtc_count > 0 else 0x00
        return f"4101 {A:02X} 00 00 00"
    elif pid == "0C":
        rpm = ENGINE_RPM_BASE
        val = int(rpm * 4)
        A = (val >> 8) & 0xFF
        B = val & 0xFF
        return f"410C {A:02X} {B:02X}"
    elif pid == "0D":
        spd = VEHICLE_SPEED & 0xFF
        return f"410D {spd:02X}"
    else:
        return "NO DATA"

def emulate():
    state = o3DIAG_ELM_ECU_EMU()
    print("o3DIAG ELM/ECU EMULATOR v3.5 for o3DIAG - Copyright (c) openw3rk INVENT\n\n"
          "https://o3diag.openw3rk.de | https://openw3rk.de\n"
          "************************************************************************\n"
          "DTCs in emulated ECU:\n"
          "---------------------\n"
          "1. Zyl.1-Misfire\n"
          "2. Bank 1 Catalytic Converter - Efficiency Below Threshold\n"
          "3. Incorrect Injection Timing\n"
          "4. Crankshaft Position/Camshaft Position, Bank 2 Sensor B - Reference Failure\n"
          "5. Intake air temperature too high\n"
          "6. Fuel Rail/System Pressure Too Low\n"
          "7. Turbocharger Compressor Control Solenoid - Open Circuit)\n"
          "--> READ via. OBD-II\n")
    print(f"\033[94m[ELM-EMU] opening {PORT} @ {BAUD}-BAUD 8N1…\nLOG:\n")
    print("\033[92mREADY\n\033[0m")
    with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
        buf = ""
        last_prompt_time = time.time()

        def write_bytes(b: bytes):
            ser.write(b)
            ser.flush()
        def write_resp_line(line_hex: str):
            write_bytes(state.fmt_line(line_hex))

        def write_text_line(text: str):
            write_bytes(state.fmt_textline(text))

        write_text_line("ELM327 v1.5")

        while True:
            try:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    try:
                        text = data.decode("ascii", errors="ignore")
                    except:
                        text = ""
                    buf += text

                    if "\r" in buf or "\n" in buf:
                        parts = buf.replace("\n", "\r").split("\r")
                        line = parts[0]
                        buf = "\r".join(parts[1:])

                        raw = line
                        cmd = strip_cmd(raw)

                        
                        if state.echo and raw:
                            ser.write((raw + ("\r\n" if state.linefeeds else "\r")).encode("ascii"))

                        if cmd.startswith("AT"):
                            at = cmd[2:]

                            if at == "Z":  
                                state = o3DIAG_ELM_ECU_EMU()
                                write_text_line("ELM327 v1.5")
                                continue
                            if at == "I":  
                                write_text_line("ELM327 v1.5")
                                continue
                            if at == "@1":
                                write_text_line("OBDII to RS232 Interpreter")
                                continue
                            if at == "@2":
                                write_text_line("ELM327 Emulator")
                                continue
                            if at.startswith("E"):  
                                state.echo = (at == "E1")
                                write_text_line("OK")
                                continue
                            if at.startswith("L"):  
                                state.linefeeds = (at == "L1")
                                write_text_line("OK")
                                continue
                            if at.startswith("H"):  
                                state.headers = (at == "H1")
                                write_text_line("OK")
                                continue
                            if at.startswith("S"):  
                                state.spaces = (at == "S1")
                                write_text_line("OK")
                                continue
                            if at.startswith("SP"): 
                                state.protocol = 0  
                                write_text_line("OK")
                                continue
                            if at == "DP":  
                                write_text_line("AUTO, ISO 15765-4 (CAN 11/500)")
                                continue
                            if at == "DPN":  
                                write_text_line("A0")
                                continue
                            if at == "RV":  
                                write_text_line(f"{state.voltage:.1f}V")
                                continue
                            if at == "D": 
                                state = o3DIAG_ELM_ECU_EMU()
                                write_text_line("OK")
                                continue

                            write_text_line("OK")
                            continue

                        if cmd == "03":
                            resp = build_mode03_response(DTC_CODES)
                            write_resp_line(resp)
                            continue

                        if cmd.startswith("01") and len(cmd) == 4:
                            pid = cmd[2:4]
                            resp = build_mode01(pid, dtc_count=len(DTC_CODES))
                            if resp == "NO DATA":
                                write_text_line("NO DATA")
                            else:
                                write_resp_line(resp)
                            continue

                        if cmd == "0902":
                            frames = build_mode09_vin_frames(VIN)
                            for f in frames:
                                write_resp_line(f)
                                time.sleep(0.03)
                            continue
                        write_text_line("NO DATA")

                if time.time() - last_prompt_time > 5:
                    ser.write((">" if not state.linefeeds else "\r\n>").encode("ascii"))
                    last_prompt_time = time.time()
                time.sleep(0.01)

            except KeyboardInterrupt:
                print("\n[ELM-EMU] closed.")
                break
            except Exception as e:
                print("\033[91m[ELM-EMU] PANIC:", e)
                time.sleep(0.2)

if __name__ == "__main__":
    try:
        emulate()
    except serial.SerialException as e:
        print(f"[ELM-EMU] cannot open {PORT} {e}")
        sys.exit(1)
