import pygame
import src.utils.methods as umethods
from mqtt_emsd_lift import EMSDLift

def pygame_demo(lift: EMSDLift):
  pygame.init()

  speed = 10
  SCREEN_WIDTH = 600
  SCREEN_HEIGHT = 400

  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

  run = True
  while run:

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

      if event.type == pygame.KEYDOWN:
        ### CLOCKWISE
        if event.key == pygame.K_s:
          # print("moving...")
          lift.get_state()
        if event.key == pygame.K_o:
          # print("moving...")
          res = lift.open()
          print(f'press success? {res}!!')
        if event.key == pygame.K_c:
          # print("moving...")
          res = lift.close()
          print(f'press success? {res}!!')
        if event.key == pygame.K_r:
          # print("moving...")
          lift.release_all_keys() # not keep pressing
          print(f'release_all_keys')
        if event.key == pygame.K_0:
          # print("moving...")
          res = lift.to('G/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_1:
          # print("moving...")
          res = lift.to('1/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_2:
          # print("moving...")
          res = lift.to('2/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_3:
          # print("moving...")
          res = lift.to('3/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_4:
          # print("moving...")
          res = lift.to('4/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_5:
          # print("moving...")
          res = lift.to('5/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_6:
          # print("moving...")
          res = lift.to('6/F')
          print(f'press success? {res}!!')
        if event.key == pygame.K_7:
          # print("moving...")
          res = lift.to('7/F')
          print(f'press success? {res}!!')
    
        


  pygame.quit()

if __name__ == '__main__':

    '''
    c - close
    o - open
    s - get current lift status
    r - reset all keys
    0 - to ground floor
    4 - to 4th floor
    6 - to 6th floor
    '''

    config = umethods.load_config('../../conf/config.properties')

    lift = EMSDLift(config)
    lift.start()

    # print(robot1.get_current_pos_joint())
    # print(robot1.pos)
    
    pygame_demo(lift)


