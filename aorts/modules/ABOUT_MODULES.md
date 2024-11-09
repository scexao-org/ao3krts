# About modules

We have _modules_ which are a component's ecosystem
And we have _modes_ which are an array of modules working togethere to give some AO capability to the machine.

Generally, modes are exclusive.

Some modules are mutually exclusive.

I've identified 15 modules across the AO RTS:
- LOOP modules, which ensure the sanity of a CACAO loop and should be off of a single template
- A couple modules should be configurable -- reused through modes but slightly differently (mostly for NGS and LGS)
- Some modules wrap hardware I/O
- Finally some do custom AO jobs
- This is gonna be quite more complicated when we start thinking also about KWFS LGS, etc.

Modules:
- APD [HW]
- HOWFS_LOOP [LOOP, CFG]
- LOWFS_LOOP [LOOP, CFG]
- WTTOFFL [MISC]
- AU1OFFL [MISC, CFG]
- PT_APD [HW]
- PT_DAC [HW]
- IIWI [HW]
- NIR_LOOP [LOOP]
- PT_LOOP [LOOP]
- KWFS [HW]2
- KWFS_LOOP [LOOP]
- DM3K [HW]
- TTOFF_LOOP [LOOP]
- DAC40 [HW]

Exclusions because of hardware:
- DAC40 and PT_DAC
- PT_APD and APD
- PT_* and WTTOFFL, AU1_OFFL
Exclusions because of weirdness
- NIRWFS_LOOP, KWFS_LOOP, (HOWFS_LOOP + LOWFS_LOOP) mutually exclusive

And 7 modes (for now)


|            | PT  | NIR | NGS | OLGS | NLGS | TT  | KWFS | Currently exists? |
| ---------- | --- | --- | --- | ---- | ---- | --- | ---- | ----------------- |
| IIWI       |     | x   |     |      |      |     |      | Yes               |
| DAC40      | NO  | x   | x   | x    | x    | ?   | x    | Yes               |
| APD        |     |     | x   | x    | x    | ?   |      | Yes               |
| PT_APD     | x   |     | NO  | NO   | NO   |     |      | Yes               |
| PT_DAC     | x   | NO  | NO  | NO   | NO   |     | NO   | Yes               |
| DM3K       | x   | x   | x   | x    | x    | ?   | x    | Yes               |
| KWFS       |     |     |     |      |      |     | x    | Yes               |
| NIRLOOP    |     | x   |     |      |      |     |      |                   |
| HOWFSLOOP  |     |     | NGS | OLGS | NLGS | ?   |      |                   |
| LOWFSLOOP  |     |     |     | OLGS | NLGS | ?   |      |                   |
| PTLOOP     | x   |     |     |      |      |     |      |                   |
| KWFSLOOP   |     |     |     |      |      |     | x    |                   |
| TTOFF_LOOP |     | x   | x   | x    | x    | ?   | x    |                   |
| AU1OFFL    | NO  |     |     | OLGS | NLGS | ?   |      |                   |
| WTTOFFL    | NO  |     |     | x    | x    | ?   |      |                   |
