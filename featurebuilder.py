from llda import LLDA
import numpy as np
import pickle
import csv

TRAINING_FILES = {'tweets': 'data/generated/training_tweets.txt', 'linkedin': 'data/generated/training_linkedin.txt'}
TESTING_FILES = {'linkedin': 'data/generated/testing_linkedin.txt'}
PHI_FILES = {'tweets': 'data/generated/tweets_words.txt_phi', 'linkedin': 'data/generated/linkedin_words.txt_phi'}
INTEREST_WORDS_FILES = {'tweets': 'data/generated/tweets_interest_words.txt', 'linkedin': 'data/generated/linkedin_interest_words.txt'}
TRAINING_FEATURE_FILES = {'tweets': 'data/generated/features/training_tweets_features.csv', 'linkedin': 'data/generated/features/training_linkedin_features.csv'}
TESTING_FEATURE_FILES = {'linkedin': 'data/generated/features/testing_linkedin_features.csv'}

class FeatureBuilder:
    def __init__(self):
        self.interest_words = {}
        self.interest_words['linkedin'] = self.load_llda_interest_words(PHI_FILES['linkedin'], INTEREST_WORDS_FILES['linkedin'])
        self.create_feature_vectors(TRAINING_FILES['linkedin'], TRAINING_FEATURE_FILES['linkedin'], 'linkedin')
        self.create_feature_vectors(TESTING_FILES['linkedin'], TESTING_FEATURE_FILES['linkedin'], 'linkedin')

    def load_llda_interest_words(self, words_file, output_file):
        # read llda results
        interest_words_phi = []
        for i in range(0, 20):
            interest_words_phi.append([])

        with open(words_file, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                interest = row[0]
                word = row[1]
                phi = row[2]
                if interest.isdigit():
                    interest_words_phi[int(interest)].append([word, phi])
        
        # extract top 50 words for each interest
        interest_words = []
        for words_phi in interest_words_phi:
            sorted_words_phi =  sorted(words_phi, key=lambda x: x[1])
            sorted_words_phi.reverse()
            sorted_words_phi = sorted_words_phi[:50]
            words_phi_dict = {}
            for word_phi in sorted_words_phi:
                words_phi_dict[word_phi[0]] = float(word_phi[1])
            interest_words.append(words_phi_dict)

        pickle.dump(interest_words, open(output_file, 'wb'))
        return interest_words
        
    def create_feature_vectors(self, words_file, features_file='', social_media=''):
        features = []
        with open(words_file, 'rb') as f:
            reader = csv.reader(f, delimiter=' ')
            for row in reader:
                features.append(self.create_feature_vector(row, social_media))

        # save features into csv file
        if features_file != '':
            features = np.asarray(features)
            np.savetxt(features_file, features, delimiter=',')

        return features

    def create_feature_vector(self, words, social_media):
        lda_features = [0] * 20

        for interest, words_phi_dict in enumerate(self.interest_words[social_media]):
            for word in words:
                if (word in words_phi_dict):
                    lda_features[interest] = lda_features[interest] + words_phi_dict[word]

        return lda_features


if __name__ == "__main__":
    fb = FeatureBuilder()
