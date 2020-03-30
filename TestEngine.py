from Lib.Engine import Engine

if __name__ == '__main__':
    eng = Engine()
    eng.addSubEngine(Alarm(), False)
    eng.addSubEngine(MultiSnake(), False)
    spec = SpecTrain() 
    eng.addSubEngine(spec, True)
    eng.run()
