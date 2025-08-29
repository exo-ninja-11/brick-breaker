import tkinter as tk
import random
import math
import copy

# Main class: inherit from tk.Canvas class
class Game(tk.Canvas):
    textDisplayed = False
    linesNb = 20
    seconds = 0
    lives = 3  # Add lives variable
    score = 0  # Add score variable
    combo = 0  # Add combo variable
    lastBrickDestroyed = 0  # Track time of last brick destruction


    # Bar properties
    barHeight = 20
    barSpeed = 10

    # Ball property
    ballSpeed = 8.75

    # Bricks properties
    bricks = []
    bricksWidth = 50
    bricksHeight = 20
    bricksNbByLine = 16
    
    # Moving bricks properties
    movingBricks = []  # List to track moving bricks
    movingBrickSpeed = 1  # Speed of moving bricks
    bricksColors = {
        "r": "#e74c3c",
        "g": "#2ecc71",
        "b": "#3498db",
        "t": "#1abc9c",
        "p": "#9b59b6",
        "y": "#f1c40f",
        "o": "#e67e22",
        "e": "#ff0000",  # Explosive brick (bright red)
        "m": "#ff6b35",  # Moving brick (orange-red)
    }

    # Screen properties
    screenHeight = 500
    screenWidth = bricksWidth*bricksNbByLine

    # This method initializes some attributes: the ball, the bar...
    def __init__(self, root):
        tk.Canvas.__init__(self, root, bg="#ffffff", bd=0, highlightthickness=0, relief="ridge", width=self.screenWidth, height=self.screenHeight)
        self.pack()
        self.timeContainer = self.create_text(self.screenWidth/2, self.screenHeight*4/5, text="00:00:00", fill="#cccccc", font=("Arial", 30), justify="center")
        self.livesContainer = self.create_text(self.screenWidth/2, self.screenHeight*9/10, text="Lives: 3", fill="#e74c3c", font=("Arial", 20), justify="center")
        self.scoreContainer = self.create_text(self.screenWidth*9/10, self.screenHeight*8/10, text="Score: 0", fill="#2c3e50", font=("Arial", 16), justify="center")
        self.comboContainer = self.create_text(self.screenWidth*9/10, self.screenHeight*8.5/10, text="Combo: x1", fill="#e67e22", font=("Arial", 14), justify="center")

        self.shield = self.create_rectangle(0, 0, 0, 0, width=0)
        self.bar = self.create_rectangle(0, 0, 0, 0, fill="#7f8c8d", width=0)
        self.ball = self.create_oval(0, 0, 0, 0, width=0)
        self.ballNext = self.create_oval(0, 0, 0, 0, width=0, state="hidden")
        self.level(1)
        self.nextFrame()

    # This method, called each time a level is loaded or reloaded,
    # resets all the elements properties (size, position...).
    def reset(self):
        self.barWidth = 100
        self.ballRadius = 7
        # Reset score and combo for new level
        self.score = 0
        self.combo = 0
        self.lastBrickDestroyed = 0
        self.itemconfig(self.scoreContainer, text="Score: 0")
        self.itemconfig(self.comboContainer, text="Combo: x1")
        # Reset moving bricks
        self.movingBricks = []
        self.coords(self.shield, (0, self.screenHeight-5, self.screenWidth, self.screenHeight))
        self.itemconfig(self.shield, fill=self.bricksColors["b"], state="hidden")
        self.coords(self.bar, ((self.screenWidth - self.barWidth)/2, self.screenHeight - self.barHeight, (self.screenWidth + self.barWidth)/2, self.screenHeight))
        self.coords(self.ball, (self.screenWidth/2 - self.ballRadius, self.screenHeight - self.barHeight - 2*self.ballRadius, self.screenWidth/2 + self.ballRadius, self.screenHeight - self.barHeight))
        self.itemconfig(self.ball, fill="#2c3e50")
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))
        self.effects = {
            "ballFire": [0, 0],
            "barTall": [0, 0],
            "ballTall": [0, 0],
            "shield": [0, -1],
        }
        self.effectsPrev = copy.deepcopy(self.effects)
        self.ballThrown = False
        self.keyPressed = [False, False]
        self.losed = False
        self.won = False
        self.ballAngle = math.radians(90)
        for brick in self.bricks:
            self.delete(brick)
            del brick

    # This method displays the Nth level by reading the corresponding file (N.txt).
    def level(self, level):
        self.reset()
        self.levelNum = level
        self.bricks = []
        try:
            file = open(str(level)+".txt")
            content = list(file.read().replace("\n", ""))[:(self.bricksNbByLine*self.linesNb)]
            file.close()
            for i, el in enumerate(content):
                col = i%self.bricksNbByLine
                line = i//self.bricksNbByLine
                if el != ".":
                    if el == "m":  # Moving brick
                        # Create moving brick with random direction
                        direction = random.choice([-1, 1])
                        self.createMovingBrick(col*self.bricksWidth, line*self.bricksHeight, direction)
                    else:  # Regular brick
                        self.bricks.append(self.create_rectangle(col*self.bricksWidth, line*self.bricksHeight, (col+1)*self.bricksWidth, (line+1)*self.bricksHeight, fill=self.bricksColors[el], width=2, outline="#ffffff"))
        # If there is not any more level to load, the game is finished and the end of game screen is displayed (with player time).
        except IOError:
            self.displayText("GAME ENDED IN\n" + "%02d mn %02d sec %02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100), hide = False)
            return
        self.displayText("LEVEL\n"+str(self.levelNum))

    # This method, called each 1/60 of seconde, computes again
    # the properties of all elements (positions, collisions, effects...).
    def nextFrame(self):
        if self.ballThrown and not(self.textDisplayed):
            self.moveBall()

        if not(self.textDisplayed):
            self.updateTime()
            
        self.updateEffects()
        self.updateParticles()
        self.updateMovingBricks()

        if self.keyPressed[0]:
            self.moveBar(-game.barSpeed)
        elif self.keyPressed[1]:
            self.moveBar(game.barSpeed)

        if not(self.textDisplayed):
            if self.won:
                self.displayText("LEVEL COMPLETE!\nScore: " + str(self.score), callback = lambda: self.level(self.levelNum+1))
            elif self.losed:
                if self.lives > 0:
                    self.lives -= 1
                    self.itemconfig(self.livesContainer, text="Lives: " + str(self.lives))
                    self.displayText("LOST! Lives remaining: " + str(self.lives), callback = lambda: self.resetLevel())
                else:
                    self.displayText("GAME OVER!\nFinal Score: " + str(self.score) + "\nFinal Time: " + "%02d:%02d:%02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100), hide = False)
        
        self.after(int(1000/60), self.nextFrame)

    # This method resets the level without changing the level number
    def resetLevel(self):
        self.reset()
        self.bricks = []
        try:
            file = open(str(self.levelNum)+".txt")
            content = list(file.read().replace("\n", ""))[:(self.bricksNbByLine*self.linesNb)]
            file.close()
            for i, el in enumerate(content):
                col = i%self.bricksNbByLine
                line = i//self.bricksNbByLine
                if el != ".":
                    if el == "m":  # Moving brick
                        # Create moving brick with random direction
                        direction = random.choice([-1, 1])
                        self.createMovingBrick(col*self.bricksWidth, line*self.bricksHeight, direction)
                    else:  # Regular brick
                        self.bricks.append(self.create_rectangle(col*self.bricksWidth, line*self.bricksHeight, (col+1)*self.bricksWidth, (line+1)*self.bricksHeight, fill=self.bricksColors[el], width=2, outline="#ffffff"))
        except IOError:
            pass

    # This method handles scoring and combo system
    def addScore(self, points, isCombo=False):
        currentTime = self.seconds
        
        # Check if this is a combo (within 2 seconds of last brick)
        if isCombo and (currentTime - self.lastBrickDestroyed) < 2.0:
            self.combo += 1
        else:
            self.combo = 1
        
        # Calculate score with combo multiplier
        comboMultiplier = min(self.combo, 5)  # Cap combo at 5x
        totalPoints = points * comboMultiplier
        
        self.score += totalPoints
        self.lastBrickDestroyed = currentTime
        
        # Update display
        self.itemconfig(self.scoreContainer, text="Score: " + str(self.score))
        self.itemconfig(self.comboContainer, text="Combo: x" + str(comboMultiplier))
        
        # Show combo text if combo > 1
        if self.combo > 1:
            self.showComboText(comboMultiplier)
    
    # This method creates particle explosion effects when bricks are destroyed
    def createParticleExplosion(self, x, y, color):
        try:
            particles = []
            for i in range(8):  # Create 8 particles
                # Random direction and speed for each particle
                angle = (i * 45) + random.randint(-15, 15)  # 8 directions with some randomness
                speed = random.randint(3, 8)
                dx = speed * math.cos(math.radians(angle))
                dy = speed * math.sin(math.radians(angle))
                
                # Create small particle (small rectangle)
                particle = self.create_rectangle(
                    x, y, x + 3, y + 3, 
                    fill=color, outline="", width=0
                )
                particles.append({
                    'id': particle,
                    'dx': dx,
                    'dy': dy,
                    'life': 30  # Particle lives for 30 frames
                })
            
            # Store particles for animation
            if not hasattr(self, 'particles'):
                self.particles = []
            self.particles.extend(particles)
        except Exception as e:
            # Catch any errors to prevent crashes
            pass
    
    # This method creates flashing animation before brick disappears
    def flashBrick(self, brickId, color, callback):
        try:
            flashColors = [color, "#ffffff", color, "#ffffff", color]  # Flash between original color and white
            flashIndex = 0
            
            def flash():
                nonlocal flashIndex
                try:
                    if flashIndex < len(flashColors):
                        self.itemconfig(brickId, fill=flashColors[flashIndex])
                        flashIndex += 1
                        self.after(50, flash)  # Flash every 50ms
                    else:
                        callback()  # Execute the original destruction callback
                except Exception as e:
                    # If flashing fails, just execute the callback
                    try:
                        callback()
                    except:
                        pass
            
            flash()  # Start the flashing animation
        except Exception as e:
            # If flashing setup fails, just execute the callback
            try:
                callback()
            except:
                pass
    
    # This method updates particle positions and removes dead particles
    def updateParticles(self):
        if hasattr(self, 'particles') and self.particles:
            for particle in self.particles[:]:  # Copy list to avoid modification during iteration
                if particle['life'] > 0:
                    # Move particle
                    self.move(particle['id'], particle['dx'], particle['dy'])
                    particle['life'] -= 1
                    
                    # Fade out effect (make particle smaller as it dies)
                    if particle['life'] < 10:
                        coords = self.coords(particle['id'])
                        if len(coords) == 4:
                            centerX = (coords[0] + coords[2]) / 2
                            centerY = (coords[1] + coords[3]) / 2
                            size = max(1, particle['life'] / 10 * 3)  # Shrink particle
                            self.coords(particle['id'], 
                                      centerX - size/2, centerY - size/2,
                                      centerX + size/2, centerY + size/2)
                else:
                    # Remove dead particle
                    self.delete(particle['id'])
                    self.particles.remove(particle)
    
    # This method safely destroys a brick after effects
    def destroyBrick(self, index):
        if index < len(self.bricks):
            try:
                self.delete(self.bricks[index])
                del self.bricks[index]
            except (IndexError, tk.TclError):
                pass
    
    # This method creates a moving brick
    def createMovingBrick(self, x, y, direction=1):
        brick = self.create_rectangle(
            x, y, x + self.bricksWidth, y + self.bricksHeight,
            fill=self.bricksColors["m"], width=2, outline="#ffffff"
        )
        self.movingBricks.append({
            'id': brick,
            'x': x,
            'y': y,
            'direction': direction,  # 1 for right, -1 for left
            'speed': self.movingBrickSpeed
        })
        return brick
    
    # This method safely destroys a moving brick after effects
    def destroyMovingBrick(self, movingBrick):
        try:
            self.delete(movingBrick['id'])
            if movingBrick in self.movingBricks:
                self.movingBricks.remove(movingBrick)
        except (IndexError, tk.TclError):
            pass
    
    # This method updates moving bricks positions
    def updateMovingBricks(self):
        for movingBrick in self.movingBricks[:]:  # Copy list to avoid modification during iteration
            try:
                # Get current position
                coords = self.coords(movingBrick['id'])
                if len(coords) == 4:
                    currentX = coords[0]
                    currentY = coords[1]
                    
                    # Calculate new position
                    newX = currentX + (movingBrick['speed'] * movingBrick['direction'])
                    
                    # Check for screen edge collision
                    if newX <= 0 or newX + self.bricksWidth >= self.screenWidth:
                        # Bounce off edges
                        movingBrick['direction'] *= -1
                        newX = currentX + (movingBrick['speed'] * movingBrick['direction'])
                    
                    # Move the brick
                    self.move(movingBrick['id'], newX - currentX, 0)
                    
                    # Update stored position
                    movingBrick['x'] = newX
                    
            except (IndexError, tk.TclError):
                # Remove invalid moving brick
                self.movingBricks.remove(movingBrick)
    
    # This method shows combo text on screen
    def showComboText(self, multiplier):
        comboText = self.create_text(
            self.screenWidth/2, 
            self.screenHeight/3, 
            text="COMBO x" + str(multiplier) + "!", 
            fill="#e67e22", 
            font=("Arial", 24, "bold"), 
            justify="center"
        )
        # Remove combo text after 1 second
        self.after(1000, lambda: self.delete(comboText))

    # This method handles explosive brick explosions
    def explodeBrick(self, brickIndex):
        try:
            if brickIndex >= len(self.bricks):
                return
                
            # Get the brick's position
            brickCoords = self.coords(self.bricks[brickIndex])
            brickX = brickCoords[0] // self.bricksWidth
            brickY = brickCoords[1] // self.bricksHeight
            
            # List of bricks to destroy (including the explosive brick itself)
            bricksToDestroy = [brickIndex]
            
            # Check adjacent positions (left, right, above, below)
            adjacentPositions = [
                (brickX - 1, brickY),  # Left
                (brickX + 1, brickY),  # Right
                (brickX, brickY - 1),  # Above
                (brickX, brickY + 1),  # Below
            ]
            
            # Find and mark adjacent bricks for destruction
            for adjX, adjY in adjacentPositions:
                if 0 <= adjX < self.bricksNbByLine and 0 <= adjY < self.linesNb:
                    adjIndex = adjY * self.bricksNbByLine + adjX
                    if adjIndex < len(self.bricks) and adjIndex >= 0:
                        # Find the brick at this position
                        for j, brick in enumerate(self.bricks):
                            if j < len(self.bricks):
                                try:
                                    brickCoords = self.coords(brick)
                                    if (brickCoords[0] // self.bricksWidth == adjX and 
                                        brickCoords[1] // self.bricksHeight == adjY):
                                        if j not in bricksToDestroy:
                                            bricksToDestroy.append(j)
                                        break
                                except (IndexError, tk.TclError):
                                    continue
            
            # Destroy all marked bricks
            for index in sorted(bricksToDestroy, reverse=True):
                if index < len(self.bricks):
                    try:
                        self.addScore(10, True)  # Add 10 points for each destroyed brick
                        # Get brick position and color for effects
                        brickCoords = self.coords(self.bricks[index])
                        brickColor = self.itemcget(self.bricks[index], "fill")
                        brickX = (brickCoords[0] + brickCoords[2]) / 2
                        brickY = (brickCoords[1] + brickCoords[3]) / 2
                        # Create particle explosion and flash before destroying
                        self.createParticleExplosion(brickX, brickY, brickColor)
                        # Fix the lambda closure issue
                        current_index = index
                        self.flashBrick(self.bricks[index], brickColor, lambda idx=current_index: self.destroyBrick(idx))
                    except (IndexError, tk.TclError):
                        continue
        except Exception as e:
            # Catch any other errors to prevent crashes
            pass



    # This method, called when left or right arrows are pressed,
    # moves "x" pixels horizontally the bar, keeping it in the screen.
    # If the ball is not thrown yet, it is also moved.
    def moveBar(self, x):
        barCoords = self.coords(self.bar)
        if barCoords[0] < 10 and x < 0:
            x = -barCoords[0]
        elif barCoords[2] > self.screenWidth - 10 and x > 0:
            x = self.screenWidth - barCoords[2]
        
        self.move(self.bar, x, 0)
        if not(self.ballThrown):
            self.move(self.ball, x, 0)

    # This method, called at each frame, moves the ball.
    # It computes:
    #     - collisions between ball and bricks/bar/edge of screen
    #     - next ball position using "ballAngle" and "ballSpeed" attributes
    #     - effects to the ball and the bar during collision with special bricks
    def moveBall(self):
        # Only process collisions if the ball is actually moving
        if not self.ballThrown:
            return
            
        self.move(self.ballNext, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        ballNextCoords = self.coords(self.ballNext)
        
        # Collisions computation between ball and bricks
        i = 0
        while i < len(self.bricks):
            try:
                if i >= len(self.bricks):
                    break
                    
                collision = self.collision(self.ball, self.bricks[i])
                collisionNext = self.collision(self.ballNext, self.bricks[i])
                if not collisionNext:
                    brickColor = self.itemcget(self.bricks[i], "fill")
                    # "barTall" effect (green bricks)
                    if brickColor == self.bricksColors["g"]:
                        self.effects["barTall"][0] = 1
                        self.effects["barTall"][1] = 240
                    # "shield" effect (blue bricks)
                    elif brickColor == self.bricksColors["b"]:
                        self.effects["shield"][0] = 1
                    # "ballFire" effect (purpil bricks)
                    elif brickColor == self.bricksColors["p"]:
                        self.effects["ballFire"][0] += 1
                        self.effects["ballFire"][1] = 240
                    # "ballTall" effect (turquoise bricks)
                    elif brickColor == self.bricksColors["t"]:
                        self.effects["ballTall"][0] = 1
                        self.effects["ballTall"][1] = 240

                    if not(self.effects["ballFire"][0]):
                        if collision == 1 or collision == 3:
                            self.ballAngle = math.radians(180) - self.ballAngle
                        if collision == 2 or collision == 4:
                            self.ballAngle = -self.ballAngle
                    
                    # If the brick is red, it becomes orange.
                    if brickColor == self.bricksColors["r"]:
                        self.itemconfig(self.bricks[i], fill=self.bricksColors["o"])
                        self.addScore(10, True)  # Add 10 points for red brick
                        # Add small particle effect for color change
                        brickCoords = self.coords(self.bricks[i])
                        brickX = (brickCoords[0] + brickCoords[2]) / 2
                        brickY = (brickCoords[1] + brickCoords[3]) / 2
                        self.createParticleExplosion(brickX, brickY, brickColor)
                    # If the brick is orange, it becomes yellow.
                    elif brickColor == self.bricksColors["o"]:
                        self.itemconfig(self.bricks[i], fill=self.bricksColors["y"])
                        self.addScore(10, True)  # Add 10 points for orange brick
                        # Add small particle effect for color change
                        brickCoords = self.coords(self.bricks[i])
                        brickX = (brickCoords[0] + brickCoords[2]) / 2
                        brickY = (brickCoords[1] + brickCoords[3]) / 2
                        self.createParticleExplosion(brickX, brickY, brickColor)
                    # If the brick is explosive (bright red), it explodes and destroys adjacent bricks.
                    elif brickColor == self.bricksColors["e"]:
                        self.addScore(10, True)  # Add 10 points for explosive brick
                        # Add special explosion effect for explosive brick
                        brickCoords = self.coords(self.bricks[i])
                        brickX = (brickCoords[0] + brickCoords[2]) / 2
                        brickY = (brickCoords[1] + brickCoords[3]) / 2
                        self.createParticleExplosion(brickX, brickY, "#ff0000")  # Red explosion
                        self.explodeBrick(i)
                    # If the brick is yellow (or an other color except red/orange), it is destroyed.
                    else:
                        self.addScore(10, True)  # Add 10 points with combo potential
                        # Get brick position for particle effect
                        brickCoords = self.coords(self.bricks[i])
                        brickX = (brickCoords[0] + brickCoords[2]) / 2
                        brickY = (brickCoords[1] + brickCoords[3]) / 2
                        # Create particle explosion and flash before destroying
                        self.createParticleExplosion(brickX, brickY, brickColor)
                        # Fix the lambda closure issue by capturing the current index
                        current_index = i
                        self.flashBrick(self.bricks[i], brickColor, lambda idx=current_index: self.destroyBrick(idx))
            except (IndexError, tk.TclError, Exception) as e:
                # Skip invalid bricks and continue
                pass
            i += 1

        self.won = len(self.bricks) == 0 and len(self.movingBricks) == 0
        
        # Collisions computation between ball and moving bricks
        for movingBrick in self.movingBricks[:]:
            try:
                collision = self.collision(self.ball, movingBrick['id'])
                collisionNext = self.collision(self.ballNext, movingBrick['id'])
                if not collisionNext:
                    # Ball hit moving brick
                    if not(self.effects["ballFire"][0]):
                        if collision == 1 or collision == 3:
                            self.ballAngle = math.radians(180) - self.ballAngle
                        if collision == 2 or collision == 4:
                            self.ballAngle = -self.ballAngle
                    
                    # Destroy moving brick with effects
                    self.addScore(10, True)  # Add 10 points
                    brickCoords = self.coords(movingBrick['id'])
                    brickX = (brickCoords[0] + brickCoords[2]) / 2
                    brickY = (brickCoords[1] + brickCoords[3]) / 2
                    self.createParticleExplosion(brickX, brickY, self.bricksColors["m"])
                    self.flashBrick(movingBrick['id'], self.bricksColors["m"], lambda: self.destroyMovingBrick(movingBrick))
                    
            except (IndexError, tk.TclError):
                # Remove invalid moving brick
                self.movingBricks.remove(movingBrick)

        # Collisions computation between ball and edge of screen
        if ballNextCoords[0] < 0 or ballNextCoords[2] > self.screenWidth:
            self.ballAngle = math.radians(180) - self.ballAngle
        elif ballNextCoords[1] < 0:
            self.ballAngle = -self.ballAngle
        elif not(self.collision(self.ballNext, self.bar)):
            ballCenter = self.coords(self.ball)[0] + self.ballRadius
            barCenter = self.coords(self.bar)[0] + self.barWidth/2
            angleX = ballCenter - barCenter
            angleOrigin = (-self.ballAngle) % (3.14159*2)
            angleComputed = math.radians(-70/(self.barWidth/2)*angleX + 90)
            self.ballAngle = (1 - (abs(angleX)/(self.barWidth/2))**0.25)*angleOrigin + ((abs(angleX)/(self.barWidth/2))**0.25)*angleComputed
        elif not(self.collision(self.ballNext, self.shield)):
            if self.effects["shield"][0]:
                self.ballAngle = -self.ballAngle
                self.effects["shield"][0] = 0
            else :
                self.losed = True

        self.move(self.ball, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))

    # This method, called at each frame, manages the remaining time
    # for each of effects and displays them (bar and ball size...).
    def updateEffects(self):
        for key in self.effects.keys():
            if self.effects[key][1] > 0:
                self.effects[key][1] -= 1
            if self.effects[key][1] == 0:
                self.effects[key][0] = 0
        
        # "ballFire" effect allows the ball to destroy bricks without boucing on them.
        if self.effects["ballFire"][0]:
            self.itemconfig(self.ball, fill=self.bricksColors["p"])
        else:
            self.itemconfig(self.ball, fill="#2c3e50")

        # "barTall" effect increases the bar size.
        if self.effects["barTall"][0] != self.effectsPrev["barTall"][0]:
            diff = self.effects["barTall"][0] - self.effectsPrev["barTall"][0]
            self.barWidth += diff*60
            coords = self.coords(self.bar)
            self.coords(self.bar, tk._flatten((coords[0]-diff*30, coords[1], coords[2]+diff*30, coords[3])))
        # "ballTall" effect increases the ball size.
        if self.effects["ballTall"][0] != self.effectsPrev["ballTall"][0]:
            diff = self.effects["ballTall"][0] - self.effectsPrev["ballTall"][0]
            self.ballRadius += diff*10
            coords = self.coords(self.ball)
            self.coords(self.ball, tk._flatten((coords[0]-diff*10, coords[1]-diff*10, coords[2]+diff*10, coords[3]+diff*10)))
        
        # "shield" effect allows the ball to bounce once
        # at the bottom of the screen (it's like an additional life).
        if self.effects["shield"][0]:
            self.itemconfig(self.shield, fill=self.bricksColors["b"], state="normal")
        else:
            self.itemconfig(self.shield, state="hidden")

        self.effectsPrev = copy.deepcopy(self.effects)

    # This method updates game time (displayed in the background).
    def updateTime(self):
        self.seconds += 1/60
        self.itemconfig(self.timeContainer, text="%02d:%02d:%02d" % (int(self.seconds)//60, int(self.seconds)%60, (self.seconds*100)%100))

    # This method displays some text.
    def displayText(self, text, hide = True, callback = None):
        self.textDisplayed = True
        self.textContainer = self.create_rectangle(0, 0, self.screenWidth, self.screenHeight, fill="#ffffff", width=0, stipple="gray50")
        self.text = self.create_text(self.screenWidth/2, self.screenHeight/2, text=text, font=("Arial", 25), justify="center")
        if hide:
            self.after(3000, self.hideText)
        if callback != None:
            self.after(3000, callback)

    # This method deletes the text display.
    def hideText(self):
        self.textDisplayed = False
        self.delete(self.textContainer)
        self.delete(self.text)

    # This method computes the relative position of 2 objects that is collisions.
    def collision(self, el1, el2):
        collisionCounter = 0

        objectCoords = self.coords(el1)
        obstacleCoords = self.coords(el2)
        
        if objectCoords[2] < obstacleCoords[0] + 5:
            collisionCounter = 1
        if objectCoords[3] < obstacleCoords[1] + 5:
            collisionCounter = 2
        if objectCoords[0] > obstacleCoords[2] - 5:
            collisionCounter = 3
        if objectCoords[1] > obstacleCoords[3] - 5:
            collisionCounter = 4
                
        return collisionCounter


# This function is called on key down.
def eventsPress(event):
    global game, hasEvent

    if event.keysym == "Left":
        game.keyPressed[0] = 1
    elif event.keysym == "Right":
        game.keyPressed[1] = 1
    elif event.keysym == "space" and not(game.textDisplayed):
        game.ballThrown = True

# This function is called on key up.
def eventsRelease(event):
    global game, hasEvent
    
    if event.keysym == "Left":
        game.keyPressed[0] = 0
    elif event.keysym == "Right":
        game.keyPressed[1] = 0


# Initialization of the window
root = tk.Tk()
root.title("Brick Breaker")
root.resizable(0,0)
root.bind("<Key>", eventsPress)
root.bind("<KeyRelease>", eventsRelease)

# Starting up of the game
game = Game(root)
root.mainloop()
