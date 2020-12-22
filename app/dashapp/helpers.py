from nltk import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def format_data(pd_df):
    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = stopwords.words('english')
    # clean description data
    # step 1: lowercase
    pd_df["lower_desc"] = pd_df.job_description.str.lower()
    # step 2: remove \n
    pd_df["repl_newline"] = pd_df.lower_desc.replace("\\n", "")
    # step 3: remove punctuations and tokenize
    pd_df["tokenize"] = pd_df.apply(lambda row: tokenizer.tokenize(row['repl_newline']), axis=1)
    # step 4: remove stopwords
    pd_df['stopwords_removed'] = pd_df['tokenize'].apply(lambda x: [item for item in x if item not in stop_words])
    # step 5: merge tokens back into string text
    pd_df['clean_data'] = [" ".join(txt) for txt in pd_df["stopwords_removed"].values]
    # step 6: create bigrams
    pd_df["bigrams"] = pd_df["stopwords_removed"].apply(lambda row: list(ngrams(row, 2)))

    cv = CountVectorizer()
    cv.fit_transform(pd_df["clean_data"])
    print(len(cv.vocabulary_))


def get_most_popular_tech(pd_df):
    """
    Helper to get a consensus of most popular technologies used

    Needs access to job_description mostly
    :param pd_df:
    :return:
    """
    print(pd_df['job_description'])


def get_most_popular_language(pd_df):
    """
    Helper to get a consensus of most popular languages used

    Needs access to job_description mostly
    :param pd_df:
    :return:
    """
    print(pd_df['job_description'])


def get_skill_to_pay_comparison(pd_df):
    """
    Helper to get a consensus of a skill to pay comparison

    Needs access to job_description, salary_base
    :param pd_df:
    :return:
    """
    print(pd_df['job_description'])


def get_role_spread(pd_df):
    """
    Helper to get a consensus of most popular roles posted

    Needs access to title
    :param pd_df:
    :return:
    """
    print(pd_df['job_description'])
