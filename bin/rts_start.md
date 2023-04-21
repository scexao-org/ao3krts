# DMs and loops

### DMS
- `00` for real BIM DM
- `01` for TT DM
- `10` for simulated BIM
- `11` for simulated TT

### Loops

- `3` for NIRWFS -> BIM188
- `4` for BIM188 -> TTM

# SHM summary


### Input

- `iiwi` NIR WFS
- `iiwi-sim` improvised loop linear simulator

### DAC40 hw layer

**Inputs**
- `bim188_float`, BIM188 command in NATU (natural units, but really they're just arbitrary), as configured per `dac40_safety.h`. Symlinks over to `dm00disp`.
- `tt_value_float` TT value (idem, most likely straight volts). Symlinks to `dm01disp`.
- `wtt_value_float` WTT value (idem, but should just be 5.0, 5.0). Unused.

**Outputs**
- `bim188_tele`, command sent to DM *converted back to NATU*.
- `tt_telemetry`, command sent to TT.
- `wtt_telemetry`, command sent to WTT.s


### Misc for g2if to be happy.

Disregard entirely until we work through LGS and/or APD WFS.
But we need them to spin up the g2if OBCP/RTS communication server.

`Httg`, `Hdfg`, `LO_tt_gain`, `LO_defocus_gain`, `ADF_gain`, `ADFg`, `wttg`, `apdmatrix`, `apdcount`, `curv_ord`, `LO_tt`, `LO_defocus`.