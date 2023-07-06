from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn import datasets, linear_model
from sklearn.model_selection import cross_val_score


def train_model(training_set_path, output_model_path):
    """Trains a model from a given training set and stores it in the path given.

    Args:
        training_set_path: Path to the training set. In our case the input data come from the sklearn package so we use this patht to define where the processed data are saved.
        output_model_path: Path to a directory where the final model is stored.
    """
    diabetes_X, diabetes_y = datasets.load_diabetes(return_X_y=True, as_frame=True)

    # calculate indices to split the data manually
    nrows_all = diabetes_X.shape[0]
    nrows_no_train = 50
    nrows_leave = -20

    nrows_train = nrows_all - nrows_no_train  # all data except last 50 rows
    nrows_test = nrows_train + (nrows_no_train + nrows_leave)  # 30 rows

    # split some data to train and evaluate the training
    diabetes_X_train = diabetes_X.iloc[:nrows_train].reset_index(drop=True).copy()
    diabetes_X_test = diabetes_X.iloc[nrows_train:nrows_test].reset_index(drop=True).copy()
    diabetes_y_train = diabetes_y.iloc[:nrows_train].reset_index(drop=True).copy()
    diabetes_y_test = diabetes_y.iloc[nrows_train:nrows_test].reset_index(drop=True).copy()

    # save the processed data somewhere
    # Choose the folder path inside the repo where your model will be saved
    processed_data_path = Path(training_set_path)
    # create directory if it does not exist already
    processed_data_path.mkdir(parents=True, exist_ok=True)

    # save training data
    training_data_path = Path(processed_data_path, "training-data.csv")
    diabetes_X_train.to_csv(training_data_path, index=False)

    # save training labels
    training_labels_path = Path(processed_data_path, "training-labels.csv")
    diabetes_y_train.to_csv(training_labels_path, index=False)

    # save testing data
    testing_data_path = Path(processed_data_path, "testing-data.csv")
    diabetes_X_train.to_csv(testing_data_path, index=False)

    # save testing labels
    testing_labels_path = Path(processed_data_path, "testing-labels.csv")
    diabetes_y_train.to_csv(testing_labels_path, index=False)

    # keep some unseen data to use late as sample for inference
    # which and how much data was defined already before training the model (nrows_leave)
    diabetes_X_sample = diabetes_X.iloc[nrows_leave:].reset_index(drop=True).copy()
    diabetes_y_sample = diabetes_y.iloc[nrows_leave:].reset_index(drop=True).copy()

    # save sample data
    sample_data_path = Path(processed_data_path, "sample-inference-data.csv")
    diabetes_X_sample.to_csv(sample_data_path, index=False)

    # save sample labels (if available)
    sample_labels_path = Path(processed_data_path, "sample-inference-true-labels.csv")
    diabetes_y_sample.to_csv(sample_labels_path, index=False)

    # ----------------------------------------------------------------------------
    # Train different models

    # train model
    regr_linear = linear_model.LinearRegression()
    regr_linear.fit(diabetes_X_train, diabetes_y_train)

    print("Linear model coefs: ", regr_linear.coef_)

    # choose alpha parameter
    regr_ridge = linear_model.Ridge()
    alphas = np.logspace(-4, -1, 6)
    scores = [
        regr_ridge.set_params(alpha=alpha)
        .fit(diabetes_X_train, diabetes_y_train)
        .score(diabetes_X_test, diabetes_y_test)
        for alpha in alphas
    ]
    best_alpha = alphas[scores.index(max(scores))]
    print("Alpha values for Ridge model: ", alphas)
    print("Scores: ", scores)
    print("Best Alpha: ", best_alpha)

    # train model
    regr_ridge = linear_model.Ridge(alpha=best_alpha)
    regr_ridge.fit(diabetes_X_train, diabetes_y_train)

    print("Ridge model coefs: ", regr_ridge.coef_)

    # choose alpha parameter
    regr_lasso = linear_model.Lasso()
    alphas = np.logspace(-4, -1, 6)
    scores = [
        regr_lasso.set_params(alpha=alpha)
        .fit(diabetes_X_train, diabetes_y_train)
        .score(diabetes_X_test, diabetes_y_test)
        for alpha in alphas
    ]
    best_alpha = alphas[scores.index(max(scores))]

    print("Alpha values for Lasso model: ", alphas)
    print("Scores: ", scores)
    print("Best Alpha: ", best_alpha)

    # train model
    regr_lasso = linear_model.Lasso(alpha=best_alpha)
    regr_lasso.fit(diabetes_X_train, diabetes_y_train)

    print("Lasso model coefs: ", regr_lasso.coef_)

    # -----------------------------------------------------
    # Select best model
    cv = 10
    models_n = 3
    model_names = ["Linear", "Ridge", "Lasso"]
    # res = np.empty((models_n, cv))
    res_df = pd.DataFrame(columns=model_names, index=range(0, cv))

    diabetes_X_cv = pd.concat([diabetes_X_train, diabetes_X_test], axis=0, ignore_index=True)
    diabetes_y_cv = pd.concat([diabetes_y_train, diabetes_y_test], axis=0, ignore_index=True)

    model_list = [regr_linear, regr_ridge, regr_lasso]

    for name, model in zip(model_names, model_list):
        _scores = cross_val_score(model, diabetes_X_cv, diabetes_y_cv, cv=cv, scoring="r2")
        res_df[name] = _scores

    title = "Cross validation (" + str(cv) + "-fold) R2 scores\n"
    print(title, res_df)

    mean_values = res_df.mean(axis=0).values
    mean_names = res_df.mean(axis=0).index.values

    best_model_name = res_df.mean(axis=0).idxmin()
    best_model_index = res_df.columns.get_loc(best_model_name)
    best_model = model_list[best_model_index]

    print("Best model is chosen: ", best_model_name)

    # TODO: I need to save these plot instead of show them
    """
    import matplotlib.pyplot as plt
    title = "Mean R2 score for each model after cross validation (" + str(cv) + "-fold)"

    plt.figure()
    plt.plot(mean_values)
    plt.xticks(np.arange(models_n), mean_names, rotation='horizontal')
    plt.title(title)
    plt.show()

    import matplotlib.pyplot as plt
    title = "Mean R2 score and std for each model after cross validation (" + str(cv) + "-fold)"

    x = np.arange(models_n)
    y = mean_values
    yerr = res_df.std(axis=0).values
    plt.figure()
    plt.plot(y)
    plt.errorbar(x, y, yerr=yerr)
    plt.xticks(x, ["linear", 'ridge', 'lasso'], rotation='horizontal')
    plt.title(title)
    plt.show()
    """

    # --------------------------------------------------------------------
    # Evaluate model
    # The mean square error
    print(
        "The mean square error of the best model: ",
        np.mean((best_model.predict(diabetes_X_test) - diabetes_y_test) ** 2),
    )

    # Explained variance score: 1 is perfect prediction
    # and 0 means that there is no linear relationship
    # between X and y.
    print(
        "The explained variance score of the best model (1 is perfect prediction): ",
        best_model.score(diabetes_X_test, diabetes_y_test),
    )

    # Save the model
    # NOTE: hwo you save and load a model depends on the model itself.
    # For sklearn model have a look at these recommendations: https://scikit-learn.org/stable/model_persistence.html

    dump(best_model, output_model_path)


def load_model(path, model_name, metadata=None):
    """Loads the model from the given path.

    Args:
        path: A string with the path to the model.
        model_name: A string with the model name.
        metadata: Optional metadata given at server startup.

    Returns:
        An object with the model already loaded.
    """
    return load(Path(path) / model_name)


def inference(model, data, metadata=None):
    """Performs inference on the given model.

    Args:
        model: The already-loaded model object, as created in load_model.
        data: The data batch converted from JSON to a python object.
        metadata: Optional metadata given at server startup.

    Returns:
        A dictionary / array with the correct output.
    """
    # NOTE: this is an example, it could be done differently, it's the decision of the MO
    # data is a pandas DataFrame
    results = model.predict(data)

    # NOTE: it cannot return a list for some strange security reasons.
    return {"results": results.tolist()}
