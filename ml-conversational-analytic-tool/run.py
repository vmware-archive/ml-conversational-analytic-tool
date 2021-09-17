# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import argparse

from sklearn.model_selection import train_test_split

from baseCNN import BaseCNN
from baseLSTM import BaseLSTM
from preProcessedDataset import PreProcessedDataset


def run(annotated_filename, dataset_filename, outcome, encoding_type, model_type, padding):
    # Setup dataset
    data = PreProcessedDataset()
    data.setupPreProcess(annotated_filename, dataset_filename)
    data.encodeData()

    # Get data for training
    if encoding_type == 'role':
        obs, res = data.getRoleMatrix(outcome, padding)
    elif encoding_type == 'role-agnostic':
        obs, res = data.getRoleAgnosticMatrix(outcome, padding)

    # Create models
    if model_type == 'CNN':
        model = BaseCNN()
    elif model_type == 'LSTM':
        model = BaseLSTM()
    if encoding_type == 'role':
        model.makeModel2D(obs[0].shape)
    elif encoding_type == 'role-agnostic':
        model.makeModel(obs[0].shape)

    # Train model
    train_obs, test_obs, train_res, test_res = train_test_split(obs, res, stratify=res, test_size=0.2)
    model.trainModel(train_obs, train_res)

    # Score model
    scores = model.scoreModel(test_obs, test_res)

    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Obtain models to determine constructive and inclusive feedback in Open source communities")
    parser.add_argument('annotated_filename', help='File location of annotated file')
    parser.add_argument('dataset_filename', help='File location of extracted dataset')
    parser.add_argument('model', help='Model type to use for training')
    parser.add_argument('outcome', help='Inclusive, Constructive, or Both')
    parser.add_argument('-roleRelevant', action='store_true', default=False,
                        help='Encoding method differentiates b/w conversation roles')
    parser.add_argument('-pad', action='store_true', default=False, help='Pad total length of each pull')

    args = parser.parse_args()
    encodingType = 'role'
    if not args.roleRelevant:
        encodingType = 'role-agnostic'

    if args.outcome != 'Both':
        run_res = run(args.annotated_filename, args.dataset_filename, args.outcome, encodingType, args.model, args.pad)
        print(run_res)
    else:
        run_res_constructive = run(args.annotated_filename, args.dataset_filename, 'Constructive', encodingType,
                                   args.model, args.pad)
        print("Constructive: {}".format(run_res_constructive))

        run_res_inclusive = run(args.annotated_filename, args.dataset_filename, 'Inclusive', encodingType, args.model,
                                args.pad)
        print("Inclusvie: {}".format(run_res_inclusive))
