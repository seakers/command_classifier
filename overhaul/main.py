import os
import pathlib
import sys
import argparse

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









def main(process, train):

    if process:
        print('--> Preprocessing Data')
        client = DataProcessing()
        client.process()


    if train:
        client = Classifier()
        client.train()
        print('--> Training Model')

    if not train and not process:
        print('--> Please input either args: --process or --train')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", help="preprocesses the data",
                        action="store_true")
    parser.add_argument("--train", help="trains the model",
                        action="store_true")
    args = parser.parse_args()
    main(args.process, args.train)










