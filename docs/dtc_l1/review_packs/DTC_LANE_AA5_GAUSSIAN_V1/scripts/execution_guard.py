"""Read-only formal registration/terminal STOP guard. Does not launch."""
from run_matrix import registration_check
if __name__=='__main__':
    registration_check()
    print('Registration identity valid; this guard does not acquire authority or launch.')
