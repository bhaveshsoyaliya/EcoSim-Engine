import numpy as np

def gaussian_plume(emission, wind_speed, stack_height):

    x = np.linspace(100, 5000, 50)
    y = np.linspace(-1000, 1000, 50)

    X, Y = np.meshgrid(x, y)

    sigma_y = 0.22 * X * (1 + 0.0001 * X) ** (-0.5)
    sigma_z = 0.20 * X

    C = (
        emission /
        (2 * np.pi * wind_speed * sigma_y * sigma_z)
    ) * np.exp(-(Y**2) / (2 * sigma_y**2))

    return X, Y, C