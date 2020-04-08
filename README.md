# LED Animations


Control your LED-Strip from your RaspberryPi using multiprocessing and an object-oriented animation creation.

Many thanks to [Jks23456](https://github.com/Jks23456) who did major work on this repository.

### Getting started   

1. Clone our Project:

   ```shell script
   git clone https://github.com/Camaendir/JB-LED.git
   ```
    
2. Move into the folder

   ```shell script
   cd JB-LED
   ```
    
3. Install necessary packets (make sure you are using python 3.x):

   ```shell script
   pip install requirements.txt
   ```
    
4. Now you can try out our TestScript, which prints the Animation to the Console:

   ```shell script
   python TestEngine.py
   ```
    
5. Connect your own LED-Strip:

    Look at the TestEngine.py file and follow the instructions in the comments

### Creating your own Animations 

1. Create a new File:

   ```shell script
   touch YOURANIMATION.py
   ```
    
2. Create a subclass of SubEngine...

   ```python
   class YOURCLASS(SubEngine):
   ```
    
3. ... and implement the necessary methods:

    ```python
   def __init__(self, name, pixellength):
       super().__init__(name, pixellength) # the super constructor needs to be called
       pass
   
   def update(self):
       # one frame has passed. Move your animation to the next one.
       # Nothing has to be returned
       pass
    
   def terminating(self):
       # Your animation is about to be terminated. Do what you need to do
       # Nothing has to be returned
       pass
   ```

4. For your animation to actually do something you have to create an object...:

   ```python
   isVisible = True
   position = 0
   content = [[255, 255, 255]] * pixellength
   obj = Object(isVisible, position, content)
   # The content can be of any length (smaller than your pixellength)
   # the content is a list of lists containing the pixels rgb values: [ [r,g,b], [r,g,b], ... ]   
   ```

5. ... and add it to your SubEngine:

    ```python
   self.addObj(obj)
   ```
   
6. To animate just change it's position and content...:

   ```python
   obj.position = 5
   obj.content = [[255, 0, 0], [0, 255, 0], [0, 0, 255]] 
   ```
 
7. ... and/or add a few more:

   ```python
   isVisible = True
   position = 0
   content = [[255, 0, 0]] * pixellength
   obj2 = Object(isVisible, position, content)
   self.addObj(obj2)
   ```
   
### Getting better

To explore what your SubEngine and Objects can do for you and what Controllers and Layers are visit our [Wiki](https://github.com/Camaendir/JB-LED/wiki) here on GitHub

Thanks for looking at our repository and happy coding
 