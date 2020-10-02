from BaseClasses.Engine import Engine
from Controller.FrameViewer import FrameViewer
from Effects.Alarm import Alarm
from Controller.LEDStrip import LEDStrip
from Effects.SpecTrain import SpecTrain
from Resources.MicrophoneData import MicrophoneData

if __name__ == '__main__':

    NumPixel = 100
    Alarm_SnakeLength = 10

    # Create a Controller
    controller = FrameViewer(NumPixel)

    # If you want to use a LED-Strip instead of the FrameViewer uncomment this code and comment the part above
    #   (this only works on an RPi)
    # stripPin = 13
    # stripDMA = 11
    # stripChanel = 1
    # stripreversed = False
    # controller = LEDStrip()
    # controller.addStrip(NumPixel, stripPin, stripDMA, stripChanel, stripreversed)

    # Create an Engine
    eng = Engine()

    # Add the correct controller
    eng.setController(controller)

    # Example for Resource Usage
    # micro = MicrophoneData()
    # eng.registerResource(micro)
    # spec = SpecTrain()
    # eng.addSubEngine(spec, True)

    # Add your SubEngines

    eng.addSubEngine(Alarm(NumPixel, Alarm_SnakeLength), True)

    # And run the whole thing
    eng.run()
