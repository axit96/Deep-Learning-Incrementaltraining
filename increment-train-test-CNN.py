import numpy as np
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from keras.layers import Flatten
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return np.array(dataX), np.array(dataY)

np.random.seed(7)

def preprocessing(data):
	scaler = MinMaxScaler(feature_range=(0, 1))
	data = scaler.fit_transform(data)
	return scaler, data

def spliting(size, look_back, data):
	train_size = int(len(data) * size)
	train, test = data[0:train_size,:], data[train_size:len(data)+10,:]
	trainX, trainY = create_dataset(train, look_back)
	testX, testY = create_dataset(test, look_back)
	trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
	testX = np.reshape(testX, (testX.shape[0], 1, trainX.shape[1]))
	return trainX, trainY, testX, testY 

def training(trainX, trainY, epoch, batch):
	model = Sequential()
	model.add(Conv1D(filters=128, kernel_size=2, activation='relu'))
	model.add(MaxPooling1D(pool_size=2))
	model.add(Flatten())
	model.add(Dense(50, activation='relu'))
	model.add(Dense(1))
	model.compile(optimizer='adam', loss='mse')
	model.fit(trainX, trainY, epochs=epoch, batch_size=batch, verbose=1)
	return model

def fitting(trainX, trainY, epoch, batch,model):
	model.fit(trainX, trainY, epochs=epoch, batch_size=batch, verbose=1)
	return model

def predicion(model, trainX, testX, trainY, testY, scaler):
	trainPredict = model.predict(trainX)
	testPredict = model.predict(testX)
	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY])
	testPredict = scaler.inverse_transform(testPredict)
	testY = scaler.inverse_transform([testY])
	return testY, testPredict, trainPredict
	
def RMSE(testY, testPredict):
	testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
	print('Test Score: %.2f RMSE' % (testScore))
	return testScore

def ploting(look_back, trainPredict, testPredict,data):
	trainPredictPlot = np.empty_like(data)
	trainPredictPlot[:, :] = np.nan
	trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
	testPredictPlot = np.empty_like(data)
	testPredictPlot[:, :] = np.nan
	testPredictPlot[len(trainPredict)+(look_back*2)+1:len(data)-1, :] = testPredict
	plt.figure(figsize=(12,5))
	plt.xticks(np.arange(0,(len(data)+int(len(data)/15)),int(len(data)/15)))
	plt.grid(color='b', ls = '-.', lw = 0.25)
	plt.gca().set_facecolor((1.0, 0.992, .816))
	plt.plot(data, 'b')
	plt.plot(testPredictPlot, 'r')
	plt.ylabel("Enter Parameter name")
	plt.xlabel("No of Samples")
	plt.title("Enter Parameter name \n Duration: enter dataset duration \n Algorithm:CNN")
	return plt

dataframe = read_csv('file name with path', usecols=["column number"])
dataset = dataframe.values
dataset = dataset.astype('float64')
print(dataset)
print(len(dataset))

look = 12
epoch = 100
batch = 10

for i in range(365*24,len(dataset)):
	scale, new_data = preprocessing(dataset[:i]) 
	trainx,trainy, testx, testy = spliting(0.8,look,new_data)
	mdel = training(trainx, trainy, epoch, batch)
	mdel.save("incremental_CNN")
	print("1st year")
	print(i)
	while(i<len(dataset)):
		scale,new_data = preprocessing(dataset[i:i+60*24])
		trainx,trainy, testx, testy = spliting(0.8,look,new_data) 
		mdel = keras.models.load_model("incremental_CNN")
		mdel = fitting(trainx, trainy, epoch, batch,mdel)
		mdel.save("incremental_CNN")
		testy, testpredict, trainpredict = predicion(mdel,trainx,testx,trainy,testy,scale)
		score = RMSE(testy,testpredict)
		print(score)
		i = i + 60*24
		print("2 month")
		print(i)
	break

scale, new_data = preprocessing(dataset)
trainx,trainy, testx, testy = spliting(0.8,look,new_data)
mdel = keras.models.load_model("incremental_CNN")
mdel = fitting(trainx, trainy, epoch, batch, mdel)
mdel.save("incremental_CNN")
testy, testpredict, trainpredict = predicion(mdel,trainx,testx,trainy,testy,scale)
score = RMSE(testy,testpredict)

plt = ploting(look,trainpredict,testpredict,dataset)
plt.show()
