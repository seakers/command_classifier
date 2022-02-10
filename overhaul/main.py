import os
import pathlib

from preprocessing.DataProcessing import DataProcessing
from neuralnet.Classifier import Classifier








def preprocess():
    print('--> Preprocessing Data')
    client = DataProcessing()
    client.process()


def train():
    client = Classifier()
    client.train()
    print('--> Training Model')









def main():
    # preprocess()
    train()
    return 0









if __name__ == '__main__':
    main()










