Controler:
    Attributs:
        pixellength Type Int
    Methods:
        setup() returns None
        setFrame(pFrame) returns None

Subengine:
    Attributs:
        None;
    Methods:
        getStates() returns ["MqTT.Topic","MqTT.Payload"]
        update() returns None
        onMessage(MqTT.Topic ,MqTT.Payload) returns None

Object:
    Attributs:
        isVisible Type Boolean
        position Type Int
        content Type List[[Int, Int, Int]]