from joblib import dump
from sklearn import datasets, svm

iris = datasets.load_iris()
X, y = iris.data, iris.target

clf = svm.SVC(gamma="scale")
clf.fit(X, y)

dump(clf, "model.joblib")
