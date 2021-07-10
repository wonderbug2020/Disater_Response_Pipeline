import pandas as pd
import sys
import re
import pickle
from sqlalchemy import create_engine

import nltk
nltk.download(['punkt', 'wordnet'])

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def load_data(database_path):
    engine = create_engine('sqlite:///data/DisasterResponse.db')
    df = pd.read_sql_table('DisasterData', engine)
    X = df.message
    y = df.drop(['id','message', 'original', 'genre'], axis=1)
    category_names = y.columns
    return X, y#, category_names


def tokenize(text):
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")

    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


def build_model(database_path):
    '''Loads in the data, splits out into training and tests sets then runs a randomforestclassifier model
    '''
    database_path = database_path
    X, y = load_data(database_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])

    # train classifier
    #pipeline.fit(X_train, y_train)

    params = {
        'clf__n_estimators': [50, 150]
    }

    cv = GridSearchCV(pipeline, param_grid=params)

    return cv


def save_model(model, model_path):
    pickle.dump(model, open('model_2.pkl', 'wb'))

def main():
    if len(sys.argv) == 3:
        database_path, model_path = sys.argv[1:]
        print('Please be paitent as the model is built')
        model = build_model(database_path)
        print(f'Saving model as: {model_path}')
        save_model(model, model_path)

if __name__ == '__main__':
    main()
