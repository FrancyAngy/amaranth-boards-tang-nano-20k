import os
import subprocess

from amaranth.build import *
from amaranth.vendor import GowinPlatform

from .resources import *


__all__ = ["TangNano20kPlatform"]


class TangNano20kPlatform(GowinPlatform):
    part          = "GW2AR-LV18QN88C8/I7"
    family        = "GW2AR-18C"
    default_clk   = "clk27"
    default_rst   = "reset"
    resources     = [
        Resource("clk27", 0, Pins("4", dir="i"),
                 Clock(27e6), Attrs(IO_TYPE="LVCMOS33")),

        Resource("clk_osc", 0, Pins("OSCH", dir="i"),
                 Clock(250e6)),

        *ButtonResources(pins="88 87", invert=True,
                         attrs=Attrs(IO_TYPE="LVCMOS33")),

        Resource("reset", 0, Pins("87", dir="i", invert=True),
                attrs=Attrs(IO_TYPE="LVCMOS33")),

        *LEDResources(pins="15 16 17 18 19 20", invert=True,
                      attrs=Attrs(IO_TYPE="LVCMOS33")),

        Resource("rgb_led", 0, Pins("79", dir="o"),
                attrs=Attrs(IO_TYPE="LVCMOS33")),

        UARTResource(0, rx="70", tx="69",
            attrs=Attrs(PULL_MODE="UP", IO_TYPE="LVCMOS33")),

        #NOTE: This interface is an extra Bit-Banged UART
        # on the J1 header
        UARTResource(1, rx="j:1:19", tx="j:1:20",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *SPIFlashResources(0,
            cs_n="60", clk="59", copi="61", cipo="62",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *SDCardResources(0,
            clk="83", cmd="84", dat0="82", dat3="85", wp_n="-",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        Resource("lcd", 0,
            Subsignal("clk", Pins("76", dir="o")),
            Subsignal("hs", Pins("25", dir="o")),
            Subsignal("vs", Pins("26", dir="o")),
            Subsignal("de", Pins("77", dir="o")),
            Subsignal("r", Pins("42 41 40 39 38", dir="o")),
            Subsignal("g", Pins("37 36 35 34 33 32", dir="o")),
            Subsignal("b", Pins("31 30 29 28 27", dir="o")),
            Attrs(IO_TYPE="LVCMOS33", DRIVE=24)),

        Resource("lcd_backlight", 0, Pins("49", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33")),

        Resource("hdmi", 0,
             Subsignal("clk", DiffPairs(p="33", n="32", dir="o")),
             Subsignal("d", DiffPairs(p="35 31 29", n="34 30 28", dir="o")),
             Subsignal("cec", Pins("27", dir="io")),
             Subsignal("hpd", Pins("26", dir="i")),
             Subsignal("scl", Pins("24", dir="io")),
             Subsignal("sda", Pins("25", dir="io")),
             Attrs(IO_TYPE="LVCMOS33D")),

        Resource("psram", 0,
             Subsignal("clk", Pins("76", dir="o")),
             Subsignal("cs", Pins("71", dir="o")),
             Subsignal("adq", Pins("72 73 74 75 70 69 68 67", dir="io")),
             Subsignal("rwds", Pins("77", dir="io")),
             Attrs(IO_TYPE="LVCMOS33"), DRIVE=24),

        Resource("audio", 0,
             Subsignal("l", Pins("j:2:17", dir="o")),
             Subsignal("r", Pins("j:2:18", dir="o")),
             Attrs(IO_TYPE="LVCMOS33")),
        
        *AnalogResources(pins="j:1:13 j:1:14 j:1:15 j:1:16",
                         attrs=Attrs(IO_TYPE="LVCMOS33")),

        #NOTE: This JTAG Interface is Bit-Banged
        Resource("jtag_pins", 0,
             Subsignal("tms", Pins("j:2:3", dir="i")),
             Subsignal("tck", Pins("j:2:4", dir="i")),
             Subsignal("tdi", Pins("j:2:5", dir="i")),
             Subsignal("tdo", Pins("j:2:6", dir="o")),
             Attrs(IO_TYPE="LVCMOS33")),

    ]
    connectors = [
            Connector("j", 1, "-  -  4  5  6  7  8  9  10 11 13 14 "
                              "15 16 17 18 19 20 21 23"),
            Connector("j", 2, "-  -  76 77 71 72 73 74 75 70 69 68 "
                              "67 53 52 51 42 41 35 34"),
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "add_options":
                "set_option -use_mspi_as_gpio 1 -use_sspi_as_gpio 1",
            "gowin_pack_opts":
                "--sspi_as_gpio --mspi_as_gpio"
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        with products.extract("{}.fs".format(name)) as bitstream_filename:
            subprocess.check_call(["openFPGALoader", "-b", "tangnano20k", bitstream_filename])


if __name__ == "__main__":
    from .test.blinky import *
    TangNano20kPlatform().build(Blinky(), do_program=True)
