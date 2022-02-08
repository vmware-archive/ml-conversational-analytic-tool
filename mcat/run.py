# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse
import tarfile
import os

from sklearn.model_selection import train_test_split

from baseCNN import BaseCNN
from baseLSTM import BaseLSTM
from preProcessedDataset import PreProcessedDataset

model_directory = 'models'

def save_model(model, name, version):
    if not os.path.exists(model_directory):
        os.makedirs(model_directory)
    model_path = "{}/{}".format(model_directory, name)
    tar_file_name = "{}-{}.tar.gz".format(name, version)
    model.saveModel(name=model_path, version=version)
    os.chdir(model_path)
    tar = tarfile.open(tar_file_name, "w:gz")
    tar.add(version)
    tar.close()
    os.chdir("../../")
    print("Model saved in {}/{}; {}/{}".format(model_path, version, model_path, tar_file_name))

def run(annotated_filename, dataset_filename, outcome, encoding_type, model_type, padding, save_name, model_ver):
    # Setup dataset
    data = PreProcessedDataset()
    data.setupPreProcess(annotated_filename, dataset_filename)
    data.encodeData()

    # Create models
    if model_type == 'LSTM':
        model = BaseLSTM()
    else:
        model = BaseCNN()

    # Get data for training
    if encoding_type == 'role':
        obs, res = data.getRoleMatrix(outcome, padding)
        model.makeModel2D(obs[0].shape)
    else:
        obs, res = data.getRoleAgnosticMatrix(outcome, padding)
        model.makeModel(obs[0].shape)

    # Train model
    train_obs, test_obs, train_res, test_res = train_test_split(obs, res, stratify=res, test_size=0.2)
    model.trainModel(train_obs, train_res)

    # Score model
    scores = model.scoreModel(test_obs, test_res)
    
    # Save model
    if save_name is not None and len(save_name) > 0:
        save_model(model=model, name=save_name+"-"+outcome, version=model_ver)

    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Obtain models to determine constructive and inclusive feedback in Open source communities")
    parser.add_argument('annotated_filename', help='File location of annotated file')
    parser.add_argument('dataset_filename', help='File location of extracted dataset')
    parser.add_argument('model', help='Model type to use for training, supported CNN and LSTM')
    parser.add_argument('outcome', help='Inclusive, Constructive, or Both')
    parser.add_argument('-save', metavar='NAME', help='Save the model using given NAME')
    parser.add_argument('-save_version', metavar='VERSION', default='001',
                        help='Together with -save NAME: save the model using given NAME and VERSION. '\
                             'If omitted, 001 is used. The parameter is ignored if -save is missing.')
    parser.add_argument('-roleRelevant', action='store_true', default=False,
                        help='Encoding method differentiates b/w conversation roles')
    parser.add_argument('-pad', action='store_true', default=False, help='Pad total length of each pull')

    args = parser.parse_args()

    if args.model != 'CNN' and args.model != 'LSTM':
        raise Exception("Model must be either CNN or LSTM")

    encodingType = 'role'
    if not args.roleRelevant:
        encodingType = 'role-agnostic'

    if args.outcome != 'Both':
        run_res = run(args.annotated_filename, args.dataset_filename, args.outcome, encodingType,
                      args.model, args.pad, args.save, args.save_version)
        print(run_res)
    else:
        run_res_constructive = run(args.annotated_filename, args.dataset_filename, 'Constructive', encodingType,
                                   args.model, args.pad, args.save, args.save_version)
        print("Constructive: {}".format(run_res_constructive))

        run_res_inclusive = run(args.annotated_filename, args.dataset_filename, 'Inclusive', encodingType,
                                args.model, args.pad, args.save, args.save_version)
        print("Inclusvie: {}".format(run_res_inclusive))
