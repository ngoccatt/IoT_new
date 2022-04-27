'''
    Create data include some pair (t, y) satisfy y = 0.5[e^(-4t) - e^(-2t) + 2]
'''
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
import tensorflow as tf
import math

# Generate random data for t and y
t_data = np.linspace(-1, 10, num=1000)
y_data = 0.5 * (np.exp(-4 * t_data) - np.exp(-2 * t_data) + 2)

'''
    Create Neural Network to approximate the root of IVP
                dy/dt + 2y = 2 - e^(-4t) with y(0) = 1
'''

# Create the model
model = keras.Sequential()
model.add(keras.layers.Dense(units=1, activation='linear', input_shape=[1]))
model.add(keras.layers.Dense(units=64, activation='elu'))
model.add(keras.layers.Dense(units=64, activation='elu'))
model.add(keras.layers.Dense(units=1, activation='linear'))
model.compile(loss='mse', optimizer="adam")

# Training
model.fit(t_data, y_data, epochs=100, verbose=1)

# Compute the output
y_predicted = model.predict(t_data)

# Display the result
plt.title('Approximation root of $\dfrac{dy}{dt} + 2y = 2 - e^{-4t}$ with ' +
          '$y(0) = 1$ by Neural Network')
plt.plot(t_data, y_data, 'b', linewidth=2, label="Actual value")
plt.plot(t_data, y_predicted, 'r', linewidth=2, label="Predicted value")
plt.legend(loc="upper right")
plt.xlabel('$t$', color="blue")
plt.ylabel('$y(t)$', color="blue")
plt.grid()


