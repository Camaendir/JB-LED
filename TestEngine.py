from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm

if __name__ == '__main__':
    eng = Engine()
    print(eng.addStrip(16, 18, 10, 0, True))
    #eng.addStrip(16, 13, 11, 1, False)
    eng.addSubEngine(Alarm(16, 3), True)
    eng.run()
