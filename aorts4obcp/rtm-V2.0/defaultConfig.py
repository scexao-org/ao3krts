#===============================================================================
# Rtm default configuration dictionary
#===============================================================================
import constants as Kst

dfltConfigD = {
        "gen": {
                "framesPerEye": {
                        "desc": "Number of data frames per mirror eye update",
                        "value": Kst.DFLT_FRAMES_PER_EYE,
                        "label": "N-dataframes per mirror eye update"
                },
                "framesPerSH": {
                        "desc": "Number of data frames per SH eye",
                        "value": Kst.DFLT_FRAMES_PER_EYE,
                        "label": "N-Dataframes per SH eye update"
                },
                "framesPerSHArrow": {
                        "desc": "N-dataframes per SH-arrow update",
                        "value": Kst.DFLT_FRAMES_PER_SHARROW,
                        "label": "Dataframes per SH-arrow update"
                },
                "framesPerMountPlot": {
                        "desc":
                                "Number of data frames per tiptilt mount plot update",
                        "value":
                                Kst.DFLT_FRAMES_PER_MOUNTPLOT,
                        "label":
                                "Dataframes per TipTilt mount plot update"
                },
                "framesPerLabel": {
                        "desc":
                                "Number of data frames per labeled-value update",
                        "value":
                                Kst.DFLT_FRAMES_PER_LABEL,
                        "label":
                                "N-dataframes per labeled value update"
                },
                "framesPerChart": {
                        "desc": "Number of data frames per stripchart update",
                        "value": Kst.DFLT_FRAMES_PER_CHART,
                        "label": "Dataframes per stripchart update"
                },
                "verbose": {
                        "desc": "Verbosity level [0-10]",
                        "value": 0,
                        "label": "Verbose"
                },
                # configuration filepath must be set in constants.py:CONFIGPATH.
                # any value set here will be overwritten by CONFIGPATH.
                "configpath": {
                        "desc": "Config-file path",
                        "value": None,
                        "label": "Config path"
                },
                "debug": {
                        "desc": "Debug level [0-10]",
                        "value": 0,
                        "label": "Debug"
                },
                "ScreenY": {
                        "desc": "Window Y startup Coordinate",
                        "value": "50",
                        "label": "Start window at screen Y Coordinate"
                },
                "ScreenX": {
                        "desc": "Window X startup coordinate",
                        "value": 10,
                        "label": "Start window at screen X Coordinate"
                },
                "port": {
                        "desc": "Realtime monitor data port",
                        "value": Kst.DFLT_DATAPORT,
                        "label": "Rtm Port"
                },
                "rtDataHost": {
                        "desc": "Realtime-data host",
                        "value": Kst.DFLT_RTD_HOST,
                        "label": "Rtd-host",
                },
                "rtDataPort": {
                        "desc": "Realtime-data command port",
                        "value": Kst.DFLT_RTD_PORT,
                        "label": "RtdCmd-port",
                },
                "stripchartTzone": {
                        "desc": "Realtime-data command port",
                        "value": Kst.DFLT_STRIPCHART_TZONE,
                        "label": "RtdCmd-port",
                },
                "stripchartHours": {
                        "desc": "N-Hours buffered by stripchart",
                        "value": Kst.DFLT_STRIPCHART_HOURS,
                        "label": "Plot buffer-size",
                },
                "stripchartBufferSize": {
                        "desc": "Sripchart buffer-size",
                        "value": Kst.DFLT_STRIPCHART_BUFFERSIZE,
                        "label": "Plot buffer-size",
                },
                "secondsScaleShift": {
                        "desc": "Sripchart Seconds-scale left-shift in seconds",
                        "value": Kst.SECONDS_SCALE_SHIFT,
                        "label": "Plot buffer-size",
                },
                "minutesScaleShift": {
                        "desc": "Sripchart Minutes-scale left-shift in seconds",
                        "value": Kst.MINUTES_SCALE_SHIFT,
                        "label": "Plot buffer-size",
                },
                "hoursScaleShift": {
                        "desc": "Sripchart Hours-scale left-shift in seconds",
                        "value": Kst.HOURS_SCALE_SHIFT,
                        "label": "Plot buffer-size",
                },

                #"connectCommand": {
                #    "desc" : "RealTime Data Connect Command",
                #    "value": Kst.RTD_CONNECT_CMD,
                #    "label": "RTD Connect Command",
                #},

                # Log filepath must be set in constants.py:LOGPATH
                #"logpath": {
                #    "desc": "Logfile filepath",
                #   "value": Kst.LOGPATH,
                #    "label": "Logfile path"
                #},
        },

        #-----------------------------------------------------------------------
        #                       stripchart settings
        #-----------------------------------------------------------------------
        "stripchart": {
                "chart1": {
                        "Id": 'SC1',
                        "fixedScaleMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE1_MAX,
                                "label": "stripchart #1 fixed-scale maximum",
                        },
                        "fixedScaleMin": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE1_MIN,
                                "label": "stripchart #1 fixed-scale minimum",
                        },
                        "zeroScaleBase": {
                                "desc": "Set minimum Y-axis scale = zero",
                                "value": Kst.DFLT_ZEROSCALEBASE,
                                "label": "ZeroScaleMin",
                        },
                        # stripchart top & bottom scale thumbwheel settings
                        "scaleWheelMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL1_MAX,
                                "label": "Scalewheel maximum",
                        },
                        "scaleWheelMin": {
                                "desc": "Minimum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL1_MIN,
                                "label": "Scalewheel minimum",
                        },
                        "scaleWheelRots": {
                                "desc": "Fixed plotscale wheel rotations",
                                "value": Kst.DFLT_SCALEWHEEL1_ROTS,
                                "label": "Scalewheel maximum",
                        },
                },
                "chart2": {
                        "Id": 'SC2',
                        "fixedScaleMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE2_MAX,
                                "label": "stripchart #2 fixed-scale maximum",
                        },
                        "fixedScaleMin": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE2_MIN,
                                "label": "stripchart #2 fixed-scale minimum",
                        },
                        "zeroScaleBase": {
                                "desc": "Set minimum Y-axis scale = zero",
                                "value": Kst.DFLT_ZEROSCALEBASE,
                                "label": "ZeroScaleMin",
                        },

                        # stripchart top & bottom scale thumbwheel settings
                        "scaleWheelMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL2_MAX,
                                "label": "Scalewheel maximum",
                        },
                        "scaleWheelMin": {
                                "desc": "Minimum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL2_MIN,
                                "label": "Scalewheel minimum",
                        },
                        "scaleWheelRots": {
                                "desc": "Fixed plotscale wheel rotations",
                                "value": Kst.DFLT_SCALEWHEEL2_ROTS,
                                "label": "Scalewheel maximum",
                        },
                },
                "chart3": {
                        "Id": 'SC3',
                        "fixedScaleMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE3_MAX,
                                "label": "stripchart #3 fixed-scale maximum",
                        },
                        "fixedScaleMin": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE3_MIN,
                                "label": "stripchart #3 fixed-scale minimum",
                        },
                        "zeroScaleBase": {
                                "desc": "Set minimum Y-axis scale = zero",
                                "value": Kst.DFLT_ZEROSCALEBASE,
                                "label": "ZeroScaleMin",
                        },
                        # stripchart top & bottom scale thumbwheel settings
                        "scaleWheelMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL3_MAX,
                                "label": "Scalewheel maximum",
                        },
                        "scaleWheelMin": {
                                "desc": "Minimum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL3_MIN,
                                "label": "Scalewheel minimum",
                        },
                        "scaleWheelRots": {
                                "desc": "Fixed plotscale wheel rotations",
                                "value": Kst.DFLT_SCALEWHEEL3_ROTS,
                                "label": "Scalewheel maximum",
                        },
                },
                "chart4": {
                        "Id": 'SC4',
                        "fixedScaleMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE4_MAX,
                                "label": "stripchart #4 fixed-scale maximum",
                        },
                        "fixedScaleMin": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_FIXEDSCALE4_MIN,
                                "label": "stripchart #4 fixed-scale minimum",
                        },
                        "zeroScaleBase": {
                                "desc": "Set minimum Y-axis scale = zero",
                                "value": Kst.DFLT_ZEROSCALEBASE,
                                "label": "ZeroScaleMin",
                        },
                        # stripchart top & bottom scale thumbwheel settings
                        "scaleWheelMax": {
                                "desc": "Maximum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL4_MAX,
                                "label": "Scalewheel maximum",
                        },
                        "scaleWheelMin": {
                                "desc": "Minimum fixed plotscale wheel value ",
                                "value": Kst.DFLT_SCALEWHEEL4_MIN,
                                "label": "Scalewheel minimum",
                        },
                        "scaleWheelRots": {
                                "desc": "Fixed plotscale wheel rotations",
                                "value": Kst.DFLT_SCALEWHEEL4_ROTS,
                                "label": "Scalewheel maximum",
                        },
                },
        },

        #-----------------------------------------------------------------------
        #                       Eye-display Values
        #-----------------------------------------------------------------------
        "dmeye": {
                'label': 'Deformable Mirror-Map',
                'desc': 'Deformable Mirror-Map',
                'dataNdx': Kst.DM_CELLDATASTART,
                "alarmHi": {
                        "desc": "dm eye high alarm threshold",
                        "label": "dm eye high alarm",
                        "value": 0.0,  #40
                        'enable': False,
                },
                "alarmLow": {
                        "desc": "dm eye low alarm threshold",
                        "label": "dm eye low alarm",
                        "value": 0.0,  # -50
                        'enable': False,
                }
        },
        "crveye": {
                'label': 'Curvature Mirror-Map',
                'desc': 'Curvature Mirror-Map',
                'dataNdx': Kst.CRV_CELLDATASTART,
                "alarmHi": {
                        "desc": "Curvature eye high alarm",
                        "label": "Curvature eye high alarm",
                        "value": 0.0,
                        'enable': False,
                },
                "alarmLow": {
                        "desc": "Curvature eye low alarm",
                        "label": "Curvature eye low alarm",
                        "value": 0.0,
                        'enable': False,
                }
        },
        "apdeye": {
                'label': 'APD Eye',
                'desc': 'Avelanche-Photo-Diode Mirror-Map',
                'dataNdx': Kst.APD_CELLDATASTART,
                "alarmHi": {
                        "desc": "Avalanche Photodiode eye high alarm threshold",
                        "label": "Apd eye high alarm",
                        'value': 0.0,
                        'enable': False,
                },
                "alarmLow": {
                        "desc": "Avalanche Photodiode eye high alarm threshold",
                        "label": "Apd eye low alarm",
                        'value': 0.0,
                        'enable': False,
                }
        },
        "sheye": {
                'label': 'Sh Miror-Map',
                "desc": "Shack Hartmann Mirror-Map",
                'dataNdx': Kst.SH_CELLDATASTART,
                "alarmHi": {
                        "desc": "Shack Hartmann eye high alarm",
                        "label": "Shack Hartmann eye high alarm",
                        "value": 0.0,
                        'enable': False,
                },
                "alarmLow": {
                        "desc": "Shack Hartmann eye low alarm",
                        "label": "Shack Hartmann eye low alarm",
                        "value": 0.0,
                        'enable': False,
                }
        },

        #-----------------------------------------------------------------------
        #                       Labelled Values
        #-----------------------------------------------------------------------
        'dmTiltX': {
                'label': 'TiltX',
                'desc': 'Deformable Mirror X-axis tilt',
                'dataNdx': Kst.DM_TTMODEX,
                'alarmHi': {
                        'desc': 'dm TiltX high alarm threshold',
                        'label': 'dm TiltX high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'dm TiltX low alarm threshold',
                        'label': 'dm TiltX low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'dmTiltY': {
                'label': 'TiltY',
                'desc': 'Deformable Mirror Y-axis tilt',
                'dataNdx': Kst.DM_TTMODEY,
                'alarmHi': {
                        'desc': 'dm TiltY high alarm threshold',
                        'label': 'dm TiltY high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'dm TiltY low alarm threshold',
                        'label': 'dm TiltY low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'dmDefocus': {
                'label': 'Defocus',
                'desc': 'Deformable Mirror Defocus',
                'dataNdx': Kst.DM_DEFOCUS,
                'alarmHi': {
                        'desc': 'dm Defocus high alarm threshold',
                        'label': 'dm Defocus high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'dm Defocus low alarm threshold',
                        'label': 'dm Defocus low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'dmMin': {
                'label': 'Min',
                'desc': 'Deformable Mirror minimum count',
                'dataNdx': Kst.DM_CELLDATAMIN,
                'alarmHi': {
                        'desc': 'dm Min high alarm threshold',
                        'label': 'dm Min high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'dm Min low alarm threshold',
                        'label': 'dm Min low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'dmMax': {
                'label': 'Max',
                'desc': 'Deformable Mirror maximum count',
                'dataNdx': Kst.DM_CELLDATAMAX,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'dm Max high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'dm Max low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'dmAvg': {
                'label': 'Avg',
                'desc': 'Deformable Mirror average count',
                'dataNdx': Kst.DM_CELLDATAAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'dm Avg high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'dm Avg low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },

        # APD Labeled values
        'apdMin': {
                'label': 'Min',
                'desc': 'Avelanche-photo-diode minimum count',
                'dataNdx': Kst.APD_CELLDATAMIN,
                'alarmHi': {
                        'desc': 'apd Min high alarm threshold',
                        'label': 'apd Min high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'apd Min low alarm threshold',
                        'label': 'apd Min low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'apdMax': {
                'label': 'Max',
                'desc': 'Avelanche-photo-diode maximum count',
                'dataNdx': Kst.APD_CELLDATAMAX,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'apd Max high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'apd Max low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'apdAvg': {
                'label': 'Avg',
                'desc': 'Avelanche-photo-diode average count',
                'dataNdx': Kst.APD_CELLDATAAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'apd Avg high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'apd Avg low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'apdRmag': {
                'label': 'Rmag',
                'desc': 'Avelanche-photo-diode R-magnitude',
                'dataNdx': Kst.APD_RMAGAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'APD Rmag high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'APD Rmag low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },

        # Crv
        'crvTiltX': {
                'label': 'TiltX',
                'desc': 'Curvature X-axis tilt',
                'dataNdx': Kst.CRV_TTMODEX,
                'alarmHi': {
                        'desc': 'Curvature TiltX high alarm threshold',
                        'label': 'Curvature TiltX high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Curvature TiltY low alarm threshold',
                        'label': 'Curvature TiltY low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'crvTiltY': {
                'label': 'TiltY',
                'desc': 'Curvature Y-axis tilt',
                'dataNdx': Kst.CRV_TTMODEY,
                'alarmHi': {
                        'desc': 'Curvature TiltY high alarm threshold',
                        'label': 'Curvature TiltY high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Curvature TiltY low alarm threshold',
                        'label': 'Curvature TiltY low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'crvDefocus': {
                'label': 'Defocus',
                'desc': 'Curvature defocus',
                'dataNdx': Kst.CRV_DEFOCUS,
                'alarmHi': {
                        'desc': 'Curvature Defocus high alarm threshold',
                        'label': 'Curvature Defocus high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Curvature Defocus low alarm threshold',
                        'label': 'Curvature Defocus low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'crvMin': {
                'label': 'Min',
                'desc': 'Curvature minimum count',
                'dataNdx': Kst.CRV_CELLDATAMIN,
                'alarmHi': {
                        'desc': 'Curvature Min high alarm threshold',
                        'label': 'Curvature Min high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Curvature Min low alarm threshold',
                        'label': 'Curvature Min low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'crvMax': {
                'label': 'Max',
                'desc': 'Curvature maximum count',
                'dataNdx': Kst.CRV_CELLDATAMAX,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'Curvature Max high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'Curvature Max low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'crvAvg': {
                'label': 'Avg',
                'desc': 'Curvature average count',
                'dataNdx': Kst.CRV_CELLDATAAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'Curvature Avg high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'Curvature Avg low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shTiltX': {
                'label': 'TiltX',
                'desc': 'Shack-Hartmann X-axis tilt',
                'dataNdx': Kst.LWF_TTMODEX,
                'alarmHi': {
                        'desc': 'sh TiltX high alarm threshold',
                        'label': 'sh TiltX high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'sh TiltY low alarm threshold',
                        'label': 'sh TiltY low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shTiltY': {
                'label': 'TiltY',
                'desc': 'Shack-Hartmann Y-axis tilt',
                'dataNdx': Kst.LWF_TTMODEY,
                'alarmHi': {
                        'desc': 'sh TiltY high alarm threshold',
                        'label': 'sh TiltY high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'sh TiltY low alarm threshold',
                        'label': 'sh TiltY low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shDefocus': {
                'label': 'Defocus',
                'desc': 'Shack-Hartmann defocus',
                'dataNdx': Kst.LWF_DEFOCUS,
                'alarmHi': {
                        'desc': 'sh Defocus high alarm threshold',
                        'label': 'sh Defocus high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'sh Defocus low alarm threshold',
                        'label': 'sh Defocus low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shMax': {
                'label': 'Max',
                'desc': 'Shack-Hartmann maximum',
                'dataNdx': Kst.LWF_DATAMAX,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'sh Max high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'sh Max low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shRmag': {
                'label': 'Rmag',
                'desc': 'Shack-Hartmann R-mag',
                'dataNdx': Kst.LWF_RMAGAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'sh Rmag high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'sh Rmag low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'shAvg': {
                'label': 'Avg',
                'desc': 'Shack-Hartmann average',
                'dataNdx': Kst.LWF_COUNTAVG,
                'alarmHi': {
                        'desc': ' ',
                        'label': 'sh Avg high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'sh Avg low alarm',
                        'value': 0.0,
                        'enable': False,
                }
        },
        'loopStatus': {
                'label': 'Status',
                'desc': 'Loop Status',
                'dataNdx': Kst.LOOPSTATUS,
                'alarmHi': {
                        'desc': ' ',
                        'label': ' ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': ' ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'dmgain': {
                'label': 'DmGain',
                'desc': 'Deformable Mirror gain',
                'dataNdx': Kst.DMGAIN,
                'alarmHi': {
                        'desc': 'Dm gain high alarm',
                        'label': 'Dm gain high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Dm gain low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'ttgain': {
                'label': 'TtGain',
                'desc': 'TipTilt gain',
                'dataNdx': Kst.TTGAIN,
                'alarmHi': {
                        'desc': 'Tiptilt gain high alarm',
                        'label': 'Tiptilt gain high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Tiptilt gain low alarm',
                        'label': 'Tiptilt gain low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'psbgain': {
                'label': 'PsbGain',
                'desc': 'PSB gain',
                'dataNdx': Kst.PSUBGAIN,
                'alarmHi': {
                        'desc': 'Psub gain high alarm',
                        'label': 'Psub gain high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Psub gain low alarm',
                        'label': 'Psub gain low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'sttgain': {
                'label': 'SttGain',
                'desc': 'STT gain',
                'dataNdx': Kst.STTGAIN,
                'alarmHi': {
                        'desc': 'Stt gain high alarm',
                        'label': 'Stt gain high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Stt gain low alarm',
                        'label': 'Stt gain low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'GsMode': {
                'label': 'GsMode',
                'desc': 'Guide-Star mode',
                'dataNdx': Kst.CTRLMTRXSIDE,
                'alarmHi': {
                        'desc': 'Guidestar mode high alarm ',
                        'label': 'Guidestar mode high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': 'Guidestar mode low alarm ',
                        'label': 'Guidestar mode low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'dmgainHold': {
                'label': 'hold',
                'desc': 'Deformable Mirror gain hold',
                'dataNdx': Kst.DMGAINHOLD,
                'alarmHi': {
                        'desc': 'Dm gain hold high alarm ',
                        'label': 'Dm gain hold high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': ' ',
                        'label': 'Dm gain hold low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'ttgainHold': {
                'label': 'hold',
                'desc': 'Tiptilt gain hold',
                'dataNdx': Kst.TTGAINHOLD,
                'alarmHi': {
                        'desc': '',
                        'label': 'TipTilt gain hold high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'TipTilt gain hold low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'psbgainHold': {
                'label': 'hold',
                'desc': 'PSB gain hold',
                'dataNdx': Kst.PSUBGAINHOLD,
                'alarmHi': {
                        'desc': '',
                        'label': 'Psub gain hold high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Psub gain hold low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'sttgainHold': {
                'label': 'hold',
                'desc': 'STT gain hold',
                'dataNdx': Kst.STTGAINHOLD,
                'alarmHi': {
                        'desc': '',
                        'label': 'Stt gain hold high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Stt gain hold low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'vmdrive': {
                'label': 'Vm Drive',
                'desc': 'VM Drive Status',
                'dataNdx': Kst.VMDRIVE,
                'alarmHi': {
                        'desc': '',
                        'label': 'Vm Drive high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Vm Drive low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'vmvolt': {
                'label': 'VmVolt',
                'desc': 'VM voltage',
                'dataNdx': Kst.VMVOLT,
                'alarmHi': {
                        'desc': '',
                        'label': 'Vm Voltage high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Vm Voltage low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'vmfreq': {
                'label': 'VmFreq',
                'desc': 'VM frequency',
                'dataNdx': Kst.VMFREQ,
                'alarmHi': {
                        'desc': '',
                        'label': 'Vm frequency high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Vm frequency low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'vmphase': {
                'label': 'VmPhase',
                'desc': 'VM Phase',
                'dataNdx': Kst.VMPHASE,
                'alarmHi': {
                        'desc': '',
                        'label': 'Vm phase high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Vm phase low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'httgain': {
                'label': 'HttGain',
                'desc': 'High-Order Wavefront Sensor TipTiltgain',
                'dataNdx': Kst.HTTGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Htt gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Htt gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'wttgain': {
                'label': 'WttGain',
                'desc': 'Wavefront Sensor TipTilt gain',
                'dataNdx': Kst.WTTGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Wtt gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Wtt gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'lttgain': {
                'label': 'LttGain',
                'desc': 'Low Order Wavefront Sensor TipTilt gain',
                'dataNdx': Kst.LTTGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Ltt gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Ltt gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'ldfgain': {
                'label': 'LdfGain',
                'desc': 'Low-order wavefront-sensor defocus gain',
                'dataNdx': Kst.LDFGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Ldf gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Ldf gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'hdfgain': {
                'label': 'HdfGain',
                'desc': 'High Order Wavefront Sensor Defocus Gain',
                'dataNdx': Kst.HDFGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Hdf gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Hdf gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'adfgain': {
                'label': 'AdfGain',
                'desc': 'Acquisition Unit #1 defocus offload Gain',
                'dataNdx': Kst.ADFGAIN,
                'alarmHi': {
                        'desc': '',
                        'label': 'Adf gain high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Adf gain low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },
        'ctrlmatrix': {
                'label': 'Ctrl Matrix',
                'desc': 'Control Matrix Guide-star mode',
                'dataNdx': Kst.CTRLMTRXSIDE,
                #'xlate'  : ((0,'NGS'),(1:'LGS)),
                'alarmHi': {
                        'desc': '',
                        'label': 'Control matrix side high alarm ',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'Control matrix side low alarm ',
                        'value': 0.0,
                        'enable': False,
                },
        },

        # dm tiptiltMount plot x
        'dmTtMountX': {
                'label': 'DM Tiptilt Mount X',
                'desc': 'Deformable Mirror TipTilt mount X-axis value',
                'dataNdx': Kst.DM_TTMOUNTX,
                'alarmHi': {
                        'desc': '',
                        'label': 'DM tiptilt-mount X high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'DM tiptilt-mount X low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },

        # dm tiptiltmount plot y
        'dmTtMountY': {
                'label': 'DM Tiptilt Mount Y',
                'desc': 'Deformable Mirror TipTilt mount Y-axis value',
                'dataNdx': Kst.DM_TTMOUNTY,
                'alarmHi': {
                        'desc': '',
                        'label': 'DM tiptilt-mount Y high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'DM tiptilt-mount Y low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },

        # wfs tiptiltmount plot x
        'wfsTtMountX': {
                'label': 'WFS Tiptilt Mount X',
                'desc': 'Wavefront Sensor TipTilt mount X-axis value',
                'dataNdx': Kst.WFS_TTCH1,
                'alarmHi': {
                        'desc': '',
                        'label': 'WFS tiptilt-mount X high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'WFS tiptilt-mount X low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },

        # wfs tiptiltmount plot y
        'wfsTtMountY': {
                'label': 'WFS Tiptilt Mount Y',
                'desc': 'Wavefront Sensor TipTilt mount Y-axis value',
                'dataNdx': Kst.WFS_TTCH2,
                'alarmHi': {
                        'desc': '',
                        'label': 'WFS tiptilt-mount Y high alarm',
                        'value': 0.0,
                        'enable': False,
                },
                'alarmLow': {
                        'desc': '',
                        'label': 'WFS tiptilt-mount Y low alarm',
                        'value': 0.0,
                        'enable': False,
                },
        },
}
