# import the necessary modules
#from time import time
import pygame, math
import matplotlib.pyplot as plt

pygame.init()

FPS = 60
WIDTH, HEIGHT = 1366, 768
FLAGS = pygame.FULLSCREEN | pygame.SCALED
#screen = pygame.display.set_mode((WIDTH, HEIGHT), FLAGS)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")
font = pygame.font.Font('freesansbold.ttf', 32)
simulation_accuracy = 2
timestep_multiplier = 0.1
time_past = 0
pause = False
velocity_data = []
time_data = []

class Planet:
  #1 au in meters
  AU = 149.6e9
  #Gravitational constant
  G = 6.67428e-11
  #Zoom
  ZOOM = 800
  #To see it on the screen we need to make the scale smaller (250 / AU) = 100 pixels on the screen
  SCALE = (250 / AU) / 20
  #Simulation time
  TIMESTEP = 86400 * timestep_multiplier
  if simulation_accuracy != 0:
    TIMESTEP /= simulation_accuracy
  #Camera posistion
  CAMERA_X = 0
  CAMERA_Y = 0
  
  def __init__(self, name, x, y, radius, color, mass):
    self.x = x
    self.y = y
    self.radius = radius
    self.color = color
    self.mass = mass

    self.name = name

    self.processed_amount = 0

    self.orbit = []
    self.sun = False
    self.distance_to_sun = 0
    
    self.destroyed = False

    self.x_vel = 0
    self.y_vel = 0
    self.velocity = 0

  def draw(self, screen, planets, tracking_number):
    #stoppa detta utanför classen för att inte updatera det lika ofta, mer optimerat!!!
    if planets.index(self) == tracking_number:
      Planet.CAMERA_X = -self.x
      Planet.CAMERA_Y = -self.y

      planet_name_text = font.render(self.name, True, (255, 255, 255))
      planet_name_text_rect = planet_name_text.get_rect()
      planet_name_text_rect.x = WIDTH - planet_name_text_rect.width          
      planet_name_text_rect.y = HEIGHT - planet_name_text_rect.height * 5.6
      screen.blit(planet_name_text, planet_name_text_rect)

      self.velocity = (self.x_vel**2 + self.y_vel**2)**0.5
      planet_velocity_text = font.render(("Velocity: " + str(round(self.velocity / 1000, 2)) + " km/s"), True, (255, 255, 255))
      planet_velocity_text_rect = planet_velocity_text.get_rect()
      planet_velocity_text_rect.x = WIDTH - planet_velocity_text_rect.width          
      planet_velocity_text_rect.y = HEIGHT - planet_velocity_text_rect.height * 4.4
      screen.blit(planet_velocity_text, planet_velocity_text_rect)

      planet_mass_text = font.render(("Mass: " + str(round(self.mass, 2)) + " kg"), True, (255, 255, 255))
      planet_mass_text_rect = planet_mass_text.get_rect()
      planet_mass_text_rect.x = WIDTH - planet_mass_text_rect.width          
      planet_mass_text_rect.y = HEIGHT - planet_mass_text_rect.height * 3.2
      screen.blit(planet_mass_text, planet_mass_text_rect)

      planet_radius_text = font.render(("Radius: " + str(round(self.radius / 1000, 2)) + " km"), True, (255, 255, 255))
      planet_radius_text_rect = planet_radius_text.get_rect()
      planet_radius_text_rect.x = WIDTH - planet_radius_text_rect.width          
      planet_radius_text_rect.y = HEIGHT - planet_radius_text_rect.height * 2.1
      screen.blit(planet_radius_text, planet_radius_text_rect)

      planet_distance_text = font.render(("Distance to sun: " + str(round(self.distance_to_sun/Planet.AU, 2)) + " au"), True, (255, 255, 255))
      planet_distance_text_rect = planet_distance_text.get_rect()
      planet_distance_text_rect.x = WIDTH - planet_distance_text_rect.width          
      planet_distance_text_rect.y = HEIGHT - planet_distance_text_rect.height
      screen.blit(planet_distance_text, planet_distance_text_rect)
      
    x = self.x * self.SCALE * self.ZOOM + WIDTH / 2 
    y = self.y * self.SCALE * self.ZOOM + HEIGHT / 2
    x += self.CAMERA_X
    y += self.CAMERA_Y

    #Tar bort prickar ifall det blir för många
    if len(self.orbit) > 300:
        self.orbit = self.orbit[50:]

        #del är långsamare
        #del self.orbit[:100]

    #Tar bort prickar desto långsamare objektet är, alla prickar behövs inte för att få en bra linje ifall den rörs långsamt (ökar performance)
    if len(self.orbit) > 500 + self.processed_amount:
        self.already_processed = self.orbit[:self.processed_amount]
        self.orbit = self.already_processed + self.orbit[self.processed_amount::math.ceil(200 / math.ceil((self.x_vel**2 + self.y_vel**2)**0.5 / 1000))]
        self.processed_amount = len(self.orbit)

        #del är långsamare
        #del self.orbit[self.processed_amount::math.ceil(200 * math.ceil((self.x_vel**2 + self.y_vel**2)**0.5 / 1000))]
        #self.processed_amount = len(self.orbit)

    if len(self.orbit) > 2:
        updated_points = []
        for point in self.orbit:
            x, y = point
            x += self.CAMERA_X
            y += self.CAMERA_Y
            x = x * self.SCALE * self.ZOOM + WIDTH / 2
            y = y * self.SCALE * self.ZOOM + HEIGHT / 2
            updated_points.append((x, y))

        pygame.draw.lines(screen, self.color, False, updated_points, 2)
    pygame.draw.circle(screen, self.color, (x, y), self.radius * self.SCALE * self.ZOOM)

  def collision(self, other):
     if self.mass >= other.mass:
        self.velocity = (self.x_vel**2 + self.y_vel**2)**0.5
        other.velocity = (other.x_vel**2 + other.y_vel**2)**0.5
        #print("time past:" + str(time_past))
        #print(self.name + " velocity:" + str(self.velocity))
        #print(other.name + " velocity:" + str(other.velocity))
        #print(self.name + " mass:" + str(self.mass))
        #print(other.name + " mass:" + str(other.mass))
        old_self_x_vel = self.x_vel
        old_self_y_vel = self.y_vel
        self.x_vel = (self.mass * self.x_vel + other.mass * other.x_vel) / (self.mass + other.mass)
        self.y_vel = (self.mass * self.y_vel + other.mass * other.y_vel) / (self.mass + other.mass)
        new_self_velocity = (self.x_vel**2 + self.y_vel**2)**0.5
        ejected_velocity_x = 0
        ejected_velocity_y = 0

        normal_angle = -math.degrees(math.atan2((other.y - self.y), (other.x - self.x)))
        other_angle = -math.degrees(math.atan2(other.y_vel, other.x_vel))
        self_angle = -math.degrees(math.atan2(old_self_y_vel, old_self_x_vel))
        new_self_angle = -math.degrees(math.atan2(self.y_vel, self.x_vel))
        if other.mass > 10e20:
          ejected_mass = 0.3 * other.mass * (other.velocity / ((2 * Planet.G * self.mass / self.radius) ** 0.5)) ** 3 * 10 ** (-2*0)
          #ejected_mass = ((0.5 * self.mass * self.velocity ** 2 + 0.5 * other.mass * other.velocity ** 2) * 0.03) / ((2 * Planet.G * self.mass) / self.radius)
        else:
           ejected_mass = 0

        self.radius = (self.radius**3 + other.radius**3) ** (1/3)

        radius_ratio = self.radius / (self.mass + other.mass)

        if ejected_mass > 0:
          ejected_radius = radius_ratio * ejected_mass
          self.radius = (self.radius**3 - ejected_radius**3) ** (1/3)
        
          ejected_velocity_x = (self.mass * self.velocity * math.cos(math.radians(self_angle)) + other.mass * other.velocity * math.cos(math.radians(other_angle)) - ((self.mass + other.mass - ejected_mass) * new_self_velocity) * math.cos(math.radians(new_self_angle))) / ejected_mass
          ejected_velocity_y = (self.mass * self.velocity * math.sin(math.radians(self_angle)) + other.mass * other.velocity * math.sin(math.radians(other_angle)) - ((self.mass + other.mass - ejected_mass) * new_self_velocity) * math.sin(math.radians(new_self_angle))) / ejected_mass
    
          planets.append(Planet(self.name + " collision debri", self.x + ((self.radius + ejected_radius) * math.cos(math.radians(-normal_angle))), self.y + ((self.radius + ejected_radius) * math.sin(math.radians(-normal_angle))), ejected_radius, other.color, ejected_mass))
          planets[-1].x_vel = ejected_velocity_x
          planets[-1].y_vel = ejected_velocity_y
        
        
        self.mass += other.mass
        #print(self.name + " new velocity:" + str(self.velocity))
        #print(self.name + " new mass:" + str(self.mass))
        #print(self.name + " collision debri velocity:" + str((ejected_velocity_x**2 + ejected_velocity_y**2)**0.5))
        #print(self.name + " collision debri mass:" + str(ejected_mass))
        planets.remove(other)
        other.destroyed = True

  def pull_apart(self, other, distance):
    center_to_center_angle = -math.degrees(math.atan2((self.y - other.y), (self.x - other.x)))
    gravitational_circle_radius = ((other.radius**2 * self.mass) / other.mass)**0.5
    intersection_formula_x = (gravitational_circle_radius**2 - other.radius**2 + distance**2) / (2 * distance)
    intersection_formula_y = (gravitational_circle_radius**2 - intersection_formula_x**2)**0.5 
    if other.radius**2 - gravitational_circle_radius**2 + intersection_formula_x**2 >= 0:
      intersection_area = gravitational_circle_radius**2 * math.asin(intersection_formula_y / gravitational_circle_radius) + other.radius**2 * math.asin(intersection_formula_y / other.radius) - intersection_formula_y * (intersection_formula_x + (other.radius**2 - gravitational_circle_radius**2 + intersection_formula_x**2)**0.5)
    else:
       intersection_area = 0
    other_area = math.pi * other.radius**2
    overlap_percentage = intersection_area / other_area
    print(overlap_percentage) 
    if overlap_percentage >= 0.01:
      pulled_mass = other.mass * overlap_percentage
      if other.mass - pulled_mass > 0:
        other.mass -= pulled_mass

      if other.mass > 0:
        pulled_radius = other.radius * overlap_percentage
        if pulled_radius < other.radius:
          other.radius = (other.radius**3 - pulled_radius**3) ** (1/3)
        else:
           pulled_radius = (pulled_radius**3 + other.radius**3) ** (1/3)
           planets.remove(other)
           other.destroyed = True
        print("pully pull")
        planets.append(Planet(other.name + "debri", other.x + ((other.radius + pulled_radius) * math.cos(math.radians(-center_to_center_angle))), other.y + ((other.radius + pulled_radius) * math.sin(math.radians(-center_to_center_angle))), pulled_radius, other.color, pulled_mass))
        planets[-1].x_vel = other.x_vel
        planets[-1].y_vel = other.y_vel
      else:
        planets.remove(other)
        other.destroyed = True
      
  def attraction(self, other): 
    other_x, other_y = other.x, other.y
    distance_x = other_x - self.x
    distance_y = other_y - self.y
    distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

    if other.sun:
        self.distance_to_sun = distance
    
    #if the distance is smaller than the required distance to pull appart the other planet, pull it apart
    #if (distance - other.radius) < ((other.radius ** 2 * self.mass) / other.mass) ** 0.5 and other.mass > 10e20:
    #  self.pull_apart(other, distance)
      
    #if the planets are touching, collide
    if isinstance(distance, complex):
       print("distance")
    if isinstance(self.radius, complex):
       print("self")
    if isinstance(other.radius, complex):
       print("other")
    if distance < self.radius + other.radius:
      self.collision(other)

    #gravitations formel
    force = self.G * self.mass * other.mass / distance ** 2
    theta = math.atan2(distance_y, distance_x)
    force_x = math.cos(theta) * force
    force_y = math.sin(theta) * force
    return force_x, force_y

  def update_posistion(self, planets):
    total_fx = total_fy = 0
    for planet in planets:
      if self == planet:
        continue

      fx, fy = self.attraction(planet)
      total_fx += fx
      total_fy += fy
    
    self.x_vel += total_fx / self.mass * self.TIMESTEP
    self.y_vel += total_fy / self.mass * self.TIMESTEP 

    self.x += self.x_vel * self.TIMESTEP
    self.y += self.y_vel * self.TIMESTEP

    self.orbit.append((self.x, self.y))
    
def main():
  run = True
  clock = pygame.time.Clock()
  tracking_number = 0
  key_press = False

  sun = Planet("Sun", 0, 0, 695700e3, (255, 255, 0), 1988500e24)
  sun.sun = True

  mercury = Planet("Mercury", 1.899489215388871e7 * 1000, 4.204165905249385e7 * 1000, 2439.4e3, (100, 100, 100), 0.330103e24)
  mercury.x_vel = -5.413285046408644e1 * 1000
  mercury.y_vel =  2.194859967736300e1 * 1000
  
  venus = Planet("Venus", 8.394938902395818e7 * 1000, -6.917236904010971e7 * 1000, 6051.8e3, (200, 0, 50), 4.86731e24)
  venus.x_vel = 2.204788069515896e1 * 1000
  venus.y_vel = 2.689364524374674e1 * 1000
  
  earth = Planet("Earth", -2.546993054069973e7 * 1000, 1.448833649541957e8 * 1000, 6371.0084e3, (0, 0, 200), 5.97217e24)
  earth.x_vel = -2.981645982255353e1 * 1000
  earth.y_vel = -5.280336055653292e0 * 1000
  
  mars = Planet("Mars",  7.752583519268439e6 * 1000, 2.337845503313959e8 * 1000, 3389.5e3, (255, 0, 0), 0.641691e24)
  mars.x_vel = -2.329168054360780e1 * 1000
  mars.y_vel = 2.985994216998675e0 * 1000
 
  jupiter = Planet("Jupiter", 7.237880904345778e8 * 1000, 1.563651758403323e8 * 1000, 69911e3, (200, 100, 100), 1898.125e24)
  jupiter.x_vel = -2.314850480846128e0 * 1000
  jupiter.y_vel = 1.339942453189634e1 * 1000
  
  saturn = Planet("Saturn", 1.218831716251734e9 * 1000, -8.235549677992053e8 * 1000, 58232e3, (200, 200, 200), 568.317e24)
  saturn.x_vel = 4.871130208409098e0 * 1000
  saturn.y_vel = 7.997670501927674e0 * 1000
  
  uranus = Planet("Uranus", 2.000085203202998e9 * 1000, 2.158258155985610e9 * 1000, 25362e3, (0, 0, 150), 86.8099e24)
  uranus.x_vel = -5.047856189542717e0 * 1000
  uranus.y_vel = 4.325459531941910e0 * 1000
  
  neptune = Planet("Neptune", 4.452161925758295e9 * 1000, -4.402383333437971e8 * 1000, 24622e3, (0, 0, 255), 102.4092e24)
  neptune.x_vel = 4.977206152514373e-1 * 1000
  neptune.y_vel = 5.456979968428931e0 * 1000
  
  old_earth = Planet("Old Earth", 0, 0, 6081e3, (0, 0, 255), 5.406e24)
  old_earth.x_vel = 4000
  theia = Planet("Theia", 0.1 * Planet.AU, 0.1 * Planet.AU, 3389.5e3, (200, 200, 200), 6.39e23)
  theia.y_vel = -4000

  #black hole with 10 solar masses
  black_hole = Planet("Black Hole", 30 * Planet.AU, 0, 24764e3, (100, 0, 200), 10 * 1988500e24)

  #average planet
  average_planet = Planet("Average Planet", 30 * Planet.AU, 0, 24547e3, (100, 0, 0), 333.2e24)

  small_asteroid = Planet("Small Asteroid", 30 * Planet.AU, 0, 1e3, (200, 200, 200), 0.004e15)
  medium_asteroid = Planet("Medium Asteroid", 30 * Planet.AU, 0, 16.5e3, (200, 200, 200), 6.69e15)
  Big_asteroid = Planet("Big Asteroid", 30 * Planet.AU, 0, 457e3, (200, 200, 200), 939.3e15)

  test_planet_one = Planet("Test 1", 0, 0, 10e8, (0, 200, 0), 10e25)
  test_planet_one.x_vel = 100
  test_planet_two = Planet("Test 2", 0.05 * Planet.AU, 0.05 * Planet.AU, 5e8, (0, 0, 200), 10e24)
  test_planet_two.y_vel = -100
  test_planet_three = Planet("Test 3", 30.5 * Planet.AU, 0 * Planet.AU, 11e8, (200, 0, 0), 10e24)
  test_planet_three.y_vel = 1000
  
  #Global är stupid men det funkar så det får va
  global planets
  planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, average_planet]
  #planets = [test_planet_one, test_planet_two]
  planets = [old_earth, theia]
  global simulation_accuracy
  global pause
  global time_past
  global timestep_multiplier

  while run:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    if pause == False:
        time_past = round(time_past + Planet.TIMESTEP / 86400 * simulation_accuracy, 2)
    time_past_text = font.render("Time past: " + str(time_past) + " days", True, (255, 255, 255))
    time_past_text_rect = time_past_text.get_rect()
    time_past_text_rect.x = 0          
    time_past_text_rect.y = HEIGHT - time_past_text_rect.height * 5
    screen.blit(time_past_text, time_past_text_rect)

    frames_text = font.render(("Fps: " + str(int(clock.get_fps()))) + " frames/s", True, (255, 255, 255))
    frames_text_rect = frames_text.get_rect()
    frames_text_rect.x = 0          
    frames_text_rect.y = HEIGHT - frames_text_rect.height * 4
    screen.blit(frames_text, frames_text_rect)

    simulation_speed_text = font.render(("Simulation Speed: " + str(int(Planet.TIMESTEP / 86400 * simulation_accuracy * clock.get_fps())) + " days/s"), True, (255, 255, 255))
    simulation_speed_text_rect = simulation_speed_text.get_rect()
    simulation_speed_text_rect.x = 0          
    simulation_speed_text_rect.y = HEIGHT - simulation_speed_text_rect.height * 3
    screen.blit(simulation_speed_text, simulation_speed_text_rect)

    timestep_text = font.render(("Timestep: " + str(round(Planet.TIMESTEP / 86400 * simulation_accuracy, 2)) + " days/frame"), True, (255, 255, 255))
    timestep_text_rect = timestep_text.get_rect()
    timestep_text_rect.x = 0          
    timestep_text_rect.y = HEIGHT - timestep_text_rect.height * 2
    screen.blit(timestep_text, timestep_text_rect)

    accuracy_text = font.render(("Accuracy: " + str(simulation_accuracy) + " timesteps/frame"), True, (255, 255, 255))
    accuracy_text_rect = accuracy_text.get_rect()
    accuracy_text_rect.x = 0          
    accuracy_text_rect.y = HEIGHT - accuracy_text_rect.height
    screen.blit(accuracy_text, accuracy_text_rect)

    keys = pygame.key.get_pressed() 
    if keys[pygame.K_UP] and key_press == False:
      key_press = True
      Planet.ZOOM *= 2
    elif keys[pygame.K_DOWN] and key_press == False:
      key_press = True
      Planet.ZOOM /= 2
      if Planet.ZOOM <= 10:
        Planet.ZOOM = 1
    elif keys[pygame.K_RIGHT] and key_press == False:
      key_press = True
      if tracking_number >= len(planets) - 1:
        tracking_number = 0
      else: 
        tracking_number += 1
    elif keys[pygame.K_LEFT] and key_press == False:
        key_press = True
        if tracking_number <= 0:
            tracking_number = len(planets) - 1
        else:
            tracking_number -= 1
    elif keys[pygame.K_z] == True and key_press == False:
        key_press = True
        timestep_multiplier -= 1
        if timestep_multiplier < 0.1:
            timestep_multiplier = 5
    elif keys[pygame.K_x] == True and key_press == False:
        key_press = True
        timestep_multiplier += 1
        if timestep_multiplier > 5:
            timestep_multiplier = 1
    elif keys[pygame.K_a] == True and key_press == False:
       key_press = True
       timestep_multiplier -= 0.1
       if timestep_multiplier < 0.1:
          timestep_multiplier = 5
    elif keys[pygame.K_s] == True and key_press == False:
       key_press = True
       timestep_multiplier += 0.1
       if timestep_multiplier > 5:
          timestep_multiplier = 0.1
    elif keys[pygame.K_c] == True and key_press == False:
        key_press = True
        if simulation_accuracy < 1:
            simulation_accuracy = 10
        else: 
            simulation_accuracy -= 1
    elif keys[pygame.K_v] == True and key_press == False:
        key_press = True
        if simulation_accuracy > 10:
            simulation_accuracy = 1
        else: 
            simulation_accuracy += 1
    elif keys[pygame.K_SPACE] == True and key_press == False:
        key_press = True
        if pause == False:
            pause = True
        else:
            pause = False
    elif keys[pygame.K_RETURN] == True and key_press == False:
        key_press = True
        data = {"velocity" : velocity_data, "time" : time_data}
        plt.figure(1)
        plt.plot(data["time"], data["velocity"])
        plt.gcf().autofmt_xdate()
        plt.title("velocity vs time")
        plt.show()
    elif keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False and keys[pygame.K_UP] == False and keys[pygame.K_DOWN] == False and keys[pygame.K_SPACE] == False and keys[pygame.K_z] == False and keys[pygame.K_x] == False and keys[pygame.K_c] == False and keys[pygame.K_v] == False and keys[pygame.K_s] == False and keys[pygame.K_a] == False and keys[pygame.K_RETURN] == False:
      key_press = False
    
    Planet.TIMESTEP = 86400 * timestep_multiplier
    if simulation_accuracy != 0:
        Planet.TIMESTEP /= simulation_accuracy

    for i in range(simulation_accuracy):
      for planet in planets:
        if pause == False:
            if planet.name == "Average Planet":
              velocity_data.append(planet.velocity)
              time_data.append(time_past)
            planet.update_posistion(planets)
            if planet.destroyed == True:
              continue
        planet.draw(screen, planets, tracking_number)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

    pygame.display.update()
  pygame.QUIT

def intro_screen():
  clock = pygame.time.Clock()
  clock.tick(FPS)
  intro = True
  enter_text_blink_timer = 0

  while intro:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        intro = False
    keys = pygame.key.get_pressed() 
    if keys[pygame.K_RETURN]:
      intro = False

    screen.fill((0, 0, 0))

    enter_text = font.render("enter to start", True, (255, 255, 255))
    enter_text_rect = enter_text.get_rect()
    enter_text_rect.x = WIDTH / 2 - enter_text_rect.width / 2
    enter_text_rect.y = HEIGHT / 2 + enter_text_rect.height
    
    name_text = font.render("Planetary Collision Simulation", True, (255, 255, 255))
    name_text_rect = name_text.get_rect()
    name_text_rect.x = WIDTH / 2 - name_text_rect.width / 2
    name_text_rect.y = HEIGHT / 2

    control_text = font.render("controlls: aszxcv, space and arrowkeys", True, (255, 255, 255))
    control_text_rect = control_text.get_rect()
    control_text_rect.x = 0
    control_text_rect.y = HEIGHT - control_text_rect.height
    
    enter_text_blink_timer += 0.05
    if enter_text_blink_timer >= 0 and enter_text_blink_timer <= 4:
      screen.blit(enter_text, enter_text_rect)
    if enter_text_blink_timer >= 8:
      enter_text_blink_timer = 0
    screen.blit(name_text, name_text_rect)
    screen.blit(control_text, control_text_rect)
    
    pygame.display.update()

#intro_screen()
main()