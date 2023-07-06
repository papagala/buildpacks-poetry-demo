from sklearn import svm
from sklearn import datasets
from joblib import dump

iris = datasets.load_iris()
X, y = iris.data, iris.target

clf = svm.SVC(gamma="scale")
clf.fit(X, y)

dump(clf, "model.joblib")
