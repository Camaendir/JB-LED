from Lib.Controller.StripArrangement import StripArrangement
from Lib.Effects.UDPSocket import UDPSocket
from Lib.Engine import Engine


if __name__ == '__main__':
    strip = StripArrangement()
    strip.addStrip(245, 13, 11, 1, False)
    strip.addStrip(205, 18, 10, 0, True)
    strip.setup()
    strip.test()
