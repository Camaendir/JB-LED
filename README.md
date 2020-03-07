#LED Animations
###Installing **LSDLED**:
1. Download https://github.com/jgarff/rpi_ws281x via git:


    git clone https://github.com/jgarff/rpi_ws281x
    
2. go to the python folder:


    cd rpi_ws281x/python
    
3. create your working file:


    touch FILENAME.py
    
4. import Engine:


    from Lib.Engine import Engine
    
5. create an Engine object and add your Subengines:


    eng = Engine()
    eng.addSubengine(YOURSUBENGINE(), True)
    eng.run()

Notice that sequencing matters. SubEngines that are added first are prioritiesed toward the once added later 

_You are ready to go_

To execute run:

    sudo PYTHONPATH=".:build/lib.linux-armv7l-2.7" python YOURFILE.py
     

###Creating Subengines

Of the bat **LSDLED** comes with a few SubEngines you can immediately add.
If you want to create your own just follow this plan.

1. Create a subclass of the Subengine class


    from Lib.SubEngine import SubEngine
    class YOURSUBENGINE(SubEngine):
    .
    .
    .
    
2. Implement the update method

    
    def update(self):
    .
    .
    .

it gets called once for every frame.
For what to do in your `update method see _Creating Animations_

###Creating Animations


1. Create an Object (inside your SubEngine)


    obj = Object()
    obj.build(ISVISIBLE, POSITION, CONTENT)
    self.addObj(obj, LAYERNUMBER)
    
An Object consists of the isVisible ``Boolean`` a Position `Ìnteger` and a Content ``List``

The Content List is a list containing multiple rgb values put into a List

example:

    
    content = [[255,255,255], [0,0,0], [-1, -1, -1]]
    
a value of [-1, -1, -1] is equivalent to transparent

2. In your update method update the position and content of your Objects

3. In Later versions the Object will support more functionality


###Controlling your Animation




