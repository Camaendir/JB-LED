from BaseClasses.Engine import Engine
from Controller.FrameViewer import FrameViewer
from Controller.Console import Console
from Effects.Alarm import Alarm
from Effects.Fading import Fading
from Controller.LEDStrip import LEDStrip

if __name__ == '__main__':

    NumPixel = 50
    Alarm_SnakeLength = 2

    # Create a Controller
    controller = FrameViewer(NumPixel)


    # If you want to use a LED-Strip instead of the FrameViewer uncomment this code and comment the part above
    #   (this only works on an RPi)
    stripPin = 10  # 10 for SPI, 13,18 for PWM
    stripDMA = 10
    stripChanel = 0
    stripReversed = False
    #controller = LEDStrip()
    #controller.addStrip(NumPixel, stripPin, stripDMA, stripChanel, stripReversed)

    # Create an Engine
    eng = Engine(enable_mqtt=True)

    # Add the correct controller
    eng.registerController(controller, 0, NumPixel)

    # Example for Resource Usage
    # micro = MicrophoneData()
    # eng.registerResource(micro)
    # spec = SpecTrain()
    # eng.addSubEngine(spec, True)

    # Add your SubEngines
    eng.addSubEngine(Fading(NumPixel-5), True, 0)
    eng.addSubEngine(Alarm(5, Alarm_SnakeLength, name="test"), True, NumPixel-5)

    # And run the whole thing
    eng.run()
