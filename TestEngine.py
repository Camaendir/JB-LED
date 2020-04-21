from BaseClasses.Engine import Engine
from Effects.Alarm import Alarm
from Controller.Console import Console
# from Lib.Controller.StripArrangement import StripArrangement

if __name__ == '__main__':
    NumPixel = 100
    Alarm_SnakeLength = 10

    # Create a Controller
    controller = Console(NumPixel)

    # If you want to use a LED-Strip instead of the console uncomment this code and comment the part above
    # stripPin = 13
    # stripDMA = 11
    # stripChanel = 1
    # stripreversed = False
    # controller = LEDStrip()
    # controller.addStrip(NumPixel, stripPin, stripDMA, stripChanel, stripreversed)

    # Create an Engine
    eng = Engine()

    # Add the correct controller
    eng.setControler(controller)

    # Add your Subengines
    eng.addSubEngine(Alarm(NumPixel, Alarm_SnakeLength), True)

    # And run the whole thing
    eng.run()
