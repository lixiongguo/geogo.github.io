import gym

class CartPoleEnvManager:
    def __init__(self, device) -> None:
      
        self.device = device
        self.env = gym.make('CartPole-v1',render_mode ='rgb_array').unwrapped
        self.env.reset() 
        self.current_screen = None
        self.current_state = None
        self.done = False

    def reset(self) -> None:
        self.current_state = self.env.reset()

    def close(self) -> None:
        self.env.close()

    def render(self):
        return self.env.render()

    def display(self):
        return self.env.display()

    def num_actions_available(self):
        return self.env.action_space.n

    def take_action(self, action: torch.Tensor) -> torch.Tensor:
       
        self.current_state, reward, self.done, _,_ = self.env.step(action.item())
        return torch.tensor([reward], device=self.device)

    def get_state(self):
        if self.done or self.current_screen is None:
            state_tensor = torch.zeros_like(
              torch.tensor(self.current_screen, device=self.device)
            ).float()
        else:
            state_tensor = torch.tensor(self.current_state, device=self.device).float()
        return state_tensor

    def num_state_features(self):
        """
        (NEW!)
          Returns the number of features included in a state returned by the Gym environment.
          This is so that we can know the size of states that will be passed to the
          network as input.
        """
        return self.env.observation_space.shape[0]
    # ------------------------------------------------------------------------------
    """
    (UPDATE!)
     We no longer need any of the functions that we previously used for
     screen processing, and so they can all be deleted. These include:
      - get_screen_height()
      - get_screen_width()
      - get_processed_screen()
      - crop_screen()
      - transform_screen_data()
      - just_starting()
    """
    def image_reset(self) -> None:
        self.env.reset()
        self.current_screen = None # for resetting the screen to the first screen

    def get_image_state(self):
        """Return the current state of the environment in the form of
           a processed image of the screen.
        """
        if self.just_starting() or self.done:
            # if we're at the start of at the end of the proccess, we initialize
            # the image as a black screen.
            self.current_screen = self.get_processed_screen()
            black_screen = torch.zeros_like(self.current_screen)
            return black_screen
        else:
            # current screen
            s1 = self.current_screen
            # call a new screen (the next screen)
            s2 = self.get_processed_screen()
            # make the next screen is the current screen
            self.current_screen = s2
            # return the difference between two screens to get the current state
            return s2 - s1

    def just_starting(self) -> bool:
        """Check whether the the current screen is None or not
            This help to check if we're at the start of the environment or not!
        """
        return self.current_screen is None

    def get_screen_height(self) -> int:
        screen = self.get_processed_screen()
        return screen.shape[2]

    def get_screen_width(self) -> int:
        screen = self.get_processed_screen()
        return screen.shape[3]

    def get_processed_screen(self):
        """Get the image's color channels then transpose the channels
        into the order of channels by height and width which what PyTorch DQN expect
        """
        screen = self.render().transpose((2, 0, 1))
        screen = self.crop_screen(screen)
        return self.transform_screen_data(screen)

    def crop_screen(self, screen):
        """Except screen and will return a cropped version of it"""
        screen_height = screen.shape[1]

        # strip off top and bottom
        top = int(screen_height * 0.4)
        bottom = int(screen_height * 0.8)
        # we cropped 40% of the top of the screen & 20% of the bottom of the screen
        screen = screen[:, top:bottom, :]

        return screen

    def transform_screen_data(self, screen):
        # Convert to float, rescale, convert to tensor
        screen = np.ascontiguousarray(screen, # This array return contiguous array of the same as screen but transformed
                                      dtype=np.float32) / 255 # these values here will be stored sequencially in the memory

        screen = torch.from_numpy(screen)

        # Use `torchvision` package to compose several image transformations
        resize = T.Compose([
                           T.ToPILImage(), # Convert the image to pill image
                           T.Resize((40,90)), # resize the image to 40x90
                           T.ToTensor() # convert it to tensor
        ])
        # Unsqueeze should add another dimension which represents the batch dim
        ## since the processed images will be passed to the dqn in batches.
        return resize(screen).unsqueeze(0).to(self.device)