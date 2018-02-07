## Transfer file from desktop to ev3dev robot
If you want to move files from your desktop to the robot:
1. Find the robot IP address on the top left side of the ev3dev robot.
2. SSH to the robot [via USB cable](http://www.ev3dev.org/docs/tutorials/connecting-to-ev3dev-with-ssh/) or [via Wi-Fi](WirelessSetup.md)
3. Open another terminal, and run ***scp /path/to/file robot@robot's IP address:/path/to/destination***
4. Put the password when asked; default password is **maker**
5. If you want to execute the files from the robot directly without SSH, run ***chmod +x /path/to/file*** when you are connected to the robot through SSH

## Establishing a Client-Server connection between robot and computer
1. Make sure you have the following files on the **computer**. They should be in the same folder. They are located 
on this repository in the [server](/server) folder.
* **SocketServer.py** - The "server" script
* **writeCSV.py** - Used to write data to a CSV file
* **Constant.py** - Holds important shared constants between client and server machines

2. Make sure you have the following Python files on the **robot**. They should be in the same folder. They are located 
on this repository in the [client](/client) folder
* **SocketClient.py** - The "client" script
* **Ev3devSetup.py** - Additional stuff to setup ev3dev robot sensors and motors
* **Constant.py** - Holds important shared constants between client and server machines
* **stopmotors.sh** - A bash script to stop motors in the event that they do not stop

3. Make sure **Constant.py** contains the IP address of the computer. The server's copy can be edited directly on the computer whereas the client's copy can be edited via ssh.
To do this, open the file and change the value to the **IPv4 address** of the computer. Provided you are connected to a shared WiFi network, this can be found by going to **Connection Information** on Linux. Below is an example of what you should see and what values you should match:
![Constant.py IP](/res/howto3.png)

4. Execute the **SocketServer.py** script in terminal. Use Python 3 (**python3 SocketServer.py**). In order for the Jupyter live tracking notebooks to work, the terminal should be opened in the **server** folder. 
5. Execute the **SocketClient.py** script. There are two main ways to execute the **SocketClient.py**:
* **Via SSH** - SSH to the robot, navigate to where **SocketClient.py** is located and execute it. Use Python 3.
* **Via the robot itself** - Using the Mindstorms brick screen, you should be able to navigate through the file system on the robot. Execute the file by selecting **SocketClient.py**.

6. If the connection is successful, you should see something like this in the terminal:
![Server-Running](/res/howto1.png)

Select an option from the printed menu by pressing the corresponding number on your keyboard. For example, press '1' on your keyboard to select **Keyboard** mode.
* **Keyboard** - Allows the user to control the robot movements with WASD controls. (Requires your cursor to be in the terminal window while running)
* **Braitenburg** - Represents a Braitenburg machine
* **Random** - Random movements by the robot
* **Controller** - Allows the user to control robot movements with joystick controller. *Added to menu as of 2nd Feb.*

7. After you have selected an option, you should see values being continuously printed on the terminal as shown below:
![Server-Result](/res/howto2.png)
* **ls** - Left light sensor value
* **rs** - Right light sensor value
* **luv** - Left ultrasound sensor value
* **ruv** - Right ultrasound sensor value
* **lm** - Left motor speed
* **rm** - Right motor speed

8. To quit, press **q** on your keyboard at any point in time. The **SocketServer.py** script should terminate on the server side, and the **SocketClient.py** script on the robot should terminate automatically.

**Note:** If the program has successfully terminated but the robot continues to move, execute the **./stopmotors.sh** bash script on the robot to force the motors to stop. This can be done through SSH or directly on the robot itself.
**THIS IS A BUG**
