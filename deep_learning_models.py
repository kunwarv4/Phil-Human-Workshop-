#Genism Library
import gensim
from gensim.models import Word2Vec  #For loading word2vec words embedding
from gensim.scripts.glove2word2vec import glove2word2vec    #For loading glove words embedding
from gensim.utils import simple_preprocess
from gensim.models.keyedvectors import KeyedVectors
from gensim.utils import tokenize
#import multiprocessing

#NlTK Libraray 
import nltk
import nltk.tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer 

#Pandas and Numpy
import pandas as pd
import numpy as np 
from numpy import array
from numpy import asarray
from numpy import zeros
import statistics 
from statistics import mean

#Keras
import keras 
from keras.layers import Embedding
from keras.models import Sequential
from keras.utils import to_categorical
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, SimpleRNN
from keras.metrics import binary_accuracy
#from keras_self_attention import SeqSelfAttention, SeqWeightedAttention
from keras.layers import Dense, Flatten, Dropout, Activation, Embedding, LSTM, Bidirectional, SimpleRNN, Conv1D, MaxPooling1D, TimeDistributed

#Sci-Kit Library 
import sklearn
from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import balanced_accuracy_score
from sklearn.random_projection import sparse_random_matrix
from sklearn.model_selection import StratifiedKFold
#from sklearn import cross_validation
#from sklearn.cross_validation import KFold
from sklearn.model_selection import KFold
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, mean_squared_error, mean_absolute_error

import matplotlib.pyplot as plt

#Miscellanious 
import argparse
import os
import io
import re
import sys
import gc
import pickle
import datetime
import tensorflow as tf
import mxnet as mx
from bert_embedding import BertEmbedding
#from keras_self_attention import SeqSelfAttention, SeqWeightedAttention
from scipy.sparse import random as sparse_random
import bert


class morbidity                                                                                                                                                                     :
    def __init__(self, target_class):
        self.target_class = target_class
        #self.train_data = pd.read_csv('/home/simaz/Vivek/work/phil_humans/n2c2/final_data_n2c2/' + target_class + '.csv', sep=';').head(100) #for server
        self.train_data = pd.read_csv('~/Desktop/n2c2/' + target_class + '.csv', sep=';').head(5) #for mac
        print(type(self.train_data), len(self.train_data), '\n', self.train_data.head(3))
        self.train_data = self.train_data.sample(frac=1)       # Shuffling the data  # do not shuffle the data when need results for enseble approach
        print(type(self.train_data), len(self.train_data), '\n', self.train_data.head(1))
        #self.attention=attention()
        self.train_texts = None
        self.train_labels = None
        self.train_encoded_doc = None
        self.tokenizer = Tokenizer()
        self.mean_length = None
        self.max_length = None
        self.vocab_size = None
        self.padded_train_data = None
        self.embedding_matrix = None
        self.model = None
        #self.embedding_path = 'fasttext-300d-2M.vec'
        self.embedding_dim = 300 # for bert=None beacus is is not defined for all other word embeddings the embedding dimension is 300. 
        #self.embedding_bin= False

    def texts_and_labels(self):
        texts = []
        labels = []
        for i,r in self.train_data.iterrows():
            texts += [r['Text'].strip().split('\n', 1)[1]]  # Remove the first row
            labels += [r['Label']]
        self.train_texts = texts
        self.train_labels = labels
        print('Details of Training Data Text:', '\n', type(self.train_texts), len(self.train_texts)) # '\n', train_text[0:3])
        print('Details of Training Data Labels:', '\n', type(self.train_labels), len(self.train_labels), '\n', self.train_labels[0:10])
        print('Labels distribution of Training Labels:', '\n', 'Zeros-', self.train_labels.count(0), 'Ones=' ,self.train_labels.count(1))
        
    def padded_encoded_text(self):
        
        # Tokenizing the Data 
        self.tokenizer.fit_on_texts(self.train_texts) #self.train_text + self.test_text
        
        # Defining the Vocab Length (Size)of Unique words
        self.vocab_size = len(self.tokenizer.word_index) + 1 # It is the input length to teh embedding layer for all word embeddings except BERT
        
        # Defining the Vocab made from Unique words
        self.my_vocab = set([w for (w,i) in self.tokenizer.word_index.items()])   #set function is used to get unique words
        print('My Vocab set version is :', '\n', type(self.my_vocab), len(self.my_vocab))
 
        #Encoding the data to integar
        self.train_encoded_doc = self.tokenizer.texts_to_sequences(self.train_texts)
        print(type(self.train_encoded_doc), len(self.train_encoded_doc)) #, '\n', self.train_encoded_doc[0:5])
        
        # Getting the Average, standard devaition & Max length of Encoded Training Data
        length_train_texts = [len(x) for x in self.train_encoded_doc]
        print ("Max length is :", max(length_train_texts))  
        print ("AVG length is :", mean(length_train_texts)) 
        print('Std dev is:', np.std(length_train_texts))
        print('mean+ sd.deviation value for train encoded text is:', '\n', int(mean(length_train_texts)) + int(np.std(length_train_texts)))
        
        self.max_length = int(mean(length_train_texts)) + int(np.std(length_train_texts)) #length of string used to input the embedding layer
        #self.max_length = int(max(length_train_texts))   #dd int esle it will give error as it will not be read
        print("assigned max_length is:", self.max_length)
        
        #Padding the Integer Encoded Data to the max_length
        self.padded_train_data = pad_sequences(self.train_encoded_doc, maxlen=self.max_length)  # Padding Input Data 
        print("Shape of Training Data is:", self.padded_train_data.shape, type(self.padded_train_data), len(self.padded_train_data),
        '\n', self.padded_train_data[0:5])   # It is the final input_text
        print("Shape of Training Label is:", type(self.train_labels), len(self.train_labels))
    
    def bert(self):
        print('BERT START', str(datetime.datetime.now()))
        # E. Using Bert Model with  Mxnet
        bert_embedding = BertEmbedding(model='bert_24_1024_16', dataset_name='book_corpus_wiki_en_cased')
        self.result = bert_embedding(self.train_texts)
        print(type(self.result))
        print(self.result[0])
        id2emd = {}
        id2word = {}
        id_n = 1
        self.embedding_dim = 0
        sequences = []
        for (vocab_list, emb_list) in self.result:
            sequence = []
            for i in range(len(vocab_list)):

                if self.embedding_dim == 0:
                    self.embedding_dim = len(emb_list[i])
                sequence += [id_n]
                id2emd[id_n] = emb_list[i]
                id2word[id_n] = vocab_list[i]
                id_n += 1
            sequences += [sequence]
       
        # Create a matrix of one embedding for each word in the Input Data
        keys = sorted(id2word.keys())
        self.embedding_matrix = np.zeros((id_n, self.embedding_dim))
        for id_key in keys:
            embedding_vector = id2emd[id_key]
            self.embedding_matrix[id_key] = embedding_vector
        print('# Embeddings loaded. Matrix size:', self.embedding_matrix.shape)
        print('MATRIX ELEMENTS', self.embedding_matrix[0:10])
        print('BERT LOADED', str(datetime.datetime.now()))
        self.vocab_size = id_n

    def word2vec(self):
        print('> loading word2vec embeddings')
        #A. Word2Vecvec Using Gensim
        word_vectors = KeyedVectors.load_word2vec_format('~/Desktop/embeddings/word2vec-GoogleNews-vectors-negative300.bin', binary=True, unicode_errors='ignore')
        # Create a matrix of one embedding for each word in the Input Data
        self.embedding_matrix = np.zeros((self.vocab_size, 300))
        for word, i in self.tokenizer.word_index.items():
            if word in word_vectors:
                embedding_vector = word_vectors[word]
                self.embedding_matrix[i] = embedding_vector
        del(word_vectors)
        print('MATRIX ELEMENTS', self.embedding_matrix[0:10])
       
    def glove(self):
        print('> loading glove embeddings')
        #B. Glove Using Gensim
        #If glove file is needed to be converted in wor2vecformat
        #glove_input_file = 'glove.6B.300d.txt'
        #word2vec_output_file = 'glove.6B.300d.word2vec.txt'
        #glove2word2vec(glove_input_file, word2vec_output_file)
        
        word_vectors = KeyedVectors.load_word2vec_format('~/Desktop/embeddings/glove.6B.300d.word2vec.txt', binary=False, unicode_errors='ignore')
        # Create a matrix of one embedding for each word in the Input Data
        self.embedding_matrix = np.zeros((self.vocab_size, 300))
        for word, i in self.tokenizer.word_index.items():
            if word in word_vectors:
                embedding_vector = word_vectors[word]
                self.embedding_matrix[i] = embedding_vector
                del(word_vectors)
        print('MATRIX ELEMENTS', self.embedding_matrix[0:10])

    def fasttext(self):
        print('> loading fasttext embeddings')
        # C. Fast Text Using Gensim 
        word_vectors = KeyedVectors.load_word2vec_format('~/Desktop/embeddings/fasttext-300d-2M.vec', binary=False, unicode_errors='ignore')
        # Create a matrix of one embedding for each word in the Input Data
        self.embedding_matrix = np.zeros((self.vocab_size, 300))
        for word, i in self.tokenizer.word_index.items():
            if word in word_vectors:
                embedding_vector = word_vectors[word]
                self.embedding_matrix[i] = embedding_vector
        del(word_vectors)
        print('MATRIX ELEMENTS', self.embedding_matrix[0:10])
        
        #embedding_bin = False   # Set True for binary and False for text word embedding
        #word_vectors = gensim.models.KeyedVectors.load_word2vec_format(self.embedding_path, embedding_bin)
        
    def domain_train(self):
        print('> loading domain embeddings')
        # D. Training the self word embedding
        word_vectors = KeyedVectors.load_word2vec_format('~/Desktop/embeddings/embedding_model.txt', binary=False, unicode_errors='ignore')
        #Create a matrix of one embedding for each word in the Input Data
        self.embedding_matrix = np.zeros((self.vocab_size, self.embedding_dim))
        for word, i in self.tokenizer.word_index.items():
            if word in word_vectors:
                embedding_vector = word_vectors[word]
                self.embedding_matrix[i] = embedding_vector
        del(word_vectors)
        print('MATRIX ELEMENTS', self.embedding_matrix[0:10])
        
    def lstm(self):
        self.model = Sequential()
        e = Embedding(self.vocab_size, 300, weights=[self.embedding_matrix], input_length=self.max_length, trainable=False)  #Using Word Embeddings
        self.model.add(e)
        self.model.add(LSTM(128, return_sequences=True, dropout=0.2))
        self.model.add(LSTM(64, return_sequences=False, dropout=0.1)) 
        #model.add(Flatten(input_shape=(1,)))
        #self.model.add(Flatten())
        #self.model.add(Dense(16))
        self.model.add(Dense(1, activation='sigmoid'))
        # Compiling the model
        self.model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy']) 
        #self.model.compile(optimizer='opt', loss='loss_fn', metrics=['accuracy'])
        # Summarizing the model
        print(self.model.summary())
        #return self.model

    def bi_lstm(self):
        self.model = Sequential()
        e = Embedding(self.vocab_size, self.embedding_dim, weights=[self.embedding_matrix], input_length=self.max_length, trainable=False) 
        self.model.add(e)
        #model.add(Dense(1, activation='sigmoid'))
        self.model.add(Bidirectional(LSTM(128, return_sequences=True, dropout=0.1)))
        self.model.add(Bidirectional(LSTM(64, return_sequences=False, dropout=0.1)))
        #self.model.add(Flatten(input_shape=(1,)))
        self.model.add(Dense(16))
        self.model.add(Dense(1, activation='sigmoid'))
        # Compiling the model
        self.model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])  
        # Summarizing the model
        #return self.model
        print(self.model.summary())
    '''
    # To reset the model method-1
    def reset_weights(model):
        session = K.get_session()
        for layer in model.layers: 
            if hasattr(layer, 'kernel_initializer'):
                layer.kernel.initializer.run(session=session)
    '''
    # To reset the model method-2
    def reset_weights(self, model_type,attention_layer):
        if model_type == 'lstm':
            self.lstm(attention_layer)
        elif model_type == 'lstm_cnn':
            self.lstm_cnn()
        elif model_type == 'bi_lstm':
            self.bi_lstm()

    def train(self,model_type,attention_layer):    
    #def train(self):
        X = self.padded_train_data  
       
        Y = np.array(self.train_labels) 

        # K-fold Validation 
        kf = KFold(n_splits=10, shuffle=False)
        kf.get_n_splits(X)
        acc = []
        p = []
        r = []
        f = []
        ba = []
        results = []
        x_train_text, x_test_text ,y_train_label,y_test_label = (None,None,None,None)
        for train_index, test_index in kf.split(X):
            print('',train_index[0:5], type(train_index))
            print(test_index[0:5], type(test_index))
            x_train_text, x_test_text=X[train_index], X[test_index]   #X=Text 
            y_train_label, y_test_label=Y[train_index], Y[test_index]  #Y=Labels
            print('The shape of x_train_text and x_test_text are:', x_train_text.shape, x_test_text.shape)
            print('The type of x_train_text and x_test_text are:', type(x_train_text), type(x_test_text))
            print('The shape of y_train_label and y_test_label are:', y_train_label.shape, y_test_label.shape)
            print('The type of y_train_label and y_test_label are:', type(y_train_label), type(y_test_label))  
            
            gc.collect()
            
            self.model.fit(x_train_text, y_train_label, epochs=20, batch_size=64, verbose=1)  #Running the model on Train Text and Train Label

            #Making prediction on test data
            print('Old evaluation:')
            pred_labels=self.model.predict_classes(x_test_text)

            print('-----The 1st Classification Report')
            print(classification_report(y_test_label, pred_labels, digits=4))

            print('-----The 1st Confusion Matrix')
            print('The confusion matrix is', '\n', confusion_matrix(y_test_label, pred_labels))
            
            print('\nOriginal classes:', y_test_label[:20], '\n', len(y_test_label), type(y_test_label))
            print('Predicted classes', pred_labels[:10], '\n', len(pred_labels), type(pred_labels))
            
            #Generating a CSV File for predicrted results 
            pred=pd.DataFrame(columns=['ID', 'Orginal Labels', self.target_class])
            pred['ID'] = test_index
            pred['Orginal Labels'] = y_test_label
            pred[self.target_class] = pred_labels
            results += [pred]
            print('The data Frame pred results ', pred[:5])

            # Computing the First Metrics Report:

            acc_binary = accuracy_score(y_test_label, pred_labels)
            p_binary = precision_score(y_test_label, pred_labels)
            r_binary = recall_score(y_test_label, pred_labels)
            f_binary = f1_score(y_test_label, pred_labels)
            b_acc = balanced_accuracy_score(y_test_label, pred_labels)
            
            print('-----The 1st Metrics Report------')
            print('>>> Accuracy:', acc_binary)
            print('>>> Precision:', p_binary)
            print('>>> Recall:', r_binary)
            print('>>> F1:', f_binary)
            print('>>> Balanced Accuracy:', b_acc)

            #Swapping the 0 an 1 of the text and predicted classes
            
            print('new method2')
            new_y_test_label = []
            new_pred_labels = []

            for each_value_1 in y_test_label:
                if(each_value_1 == 0):
                    new_y_test_label += [1]
                else:
                    new_y_test_label += [0]
                    #print(new_y_test_label)
            #print(y_test_label)    

            for each_value_1 in pred_labels:
                if(each_value_1 == 0):
                    new_pred_labels += [1]
                else:
                    new_pred_labels += [0]
            
            print('new_y_test_label:', new_y_test_label[:], '\n', type(new_y_test_label), len(new_y_test_label))
            print('new_pred_labels:', new_pred_labels[:], '\n', type(new_pred_labels), len(new_pred_labels))
            
            print('-----The 2nd Classification Report')
            print(classification_report(new_y_test_label, new_pred_labels, digits=4))

            print('-----The 2nd Confusion Matrix')
            print('The confusion matrix is', '\n', confusion_matrix(new_y_test_label, new_pred_labels))

            #Computing the new Metrics Report:
            print('Computing the new Metrics Report:')
            new_acc_binary = accuracy_score(new_y_test_label, new_pred_labels)
            new_p_binary = precision_score(new_y_test_label, new_pred_labels)
            new_r_binary = recall_score(new_y_test_label, new_pred_labels)
            new_f_binary = f1_score(new_y_test_label, new_pred_labels)
            new_b_acc = balanced_accuracy_score(new_y_test_label, new_pred_labels)

            print('-----The 2nd Metrics Report------')
            print('>>> Accuracy:', new_acc_binary)
            print('>>> Precision:', new_p_binary)
            print('>>> Recall:', new_r_binary)
            print('>>> F1:', new_f_binary)
            print('>>> Balanced Accuracy:', new_b_acc)

            print('Caluclating the mean of the both metrics')
            acc_binary = (acc_binary+new_acc_binary)/2
            p_binary = (p_binary+new_p_binary)/2
            r_binary = (r_binary+new_r_binary)/2
            f_binary = (f_binary+new_f_binary)/2
            b_acc = (b_acc+new_b_acc)/2

            acc += [acc_binary]
            p += [p_binary]
            r += [r_binary]
            f += [f_binary]
            ba += [b_acc]

            print('-----The final Metrics Report------')
            print('>>> Accuracy:', acc_binary)
            print('>>> Precision:', p_binary)
            print('>>> Recall:', r_binary)
            print('>>> F1:', f_binary)
            print('>>> Balanced Accuracy:', b_acc)
            
            #1. reset_weights(self.model)
            self.reset_weights(model_type, attention_layer)
            '''
            self.model=None
            if args.model_type == 'bi_lstm':
                #morbidity_obj.bi_lstm()
                self.model=bi_lstm()
            '''

            #sys.exit(1)
        #Printing Average Results    
        print('---- The final Averaged result after 10-fold validation: ' , self.target_class)
        print('>> Accuracy:', mean(acc)*100)
        print('>> Precision:', mean(p)*100)
        print('>> Recall:', mean(r)*100)
        print('>> F1:', mean(f)*100)
        print('>> Balanced Accuracy:', mean(ba)*100)
        pred_results = pd.concat(results, axis=0, join='inner').sort_index()   #Important Axis=0 means data will be joined coulmn to column, it mean for 10 fold there will be 10 coulmns while axis=0 is row addtion. so total rowx will  be 952 but columns will remain 1. 
        print(pred_results[0:20])
        pred_results.to_csv('~/Desktop/embeddings/' + self.target_class + '_pred_results.csv', index=False)
        #pred_results.to_csv('/home/simaz/Vivek/work/' + self.target_class + '_viv_results.csv', index=False)

if __name__ == "__main__":
    print(sys.argv)
    parser =  argparse.ArgumentParser(description = "Arguments")
    parser.add_argument('--target-class', dest='target_class', default='Asthma', type=str, action='store', help='The bla bla')
    parser.add_argument('--word-embedding', dest='word_embedding', default='fasttext', type=str, action='store', help='The input file')
    parser.add_argument('--model-type', dest='model_type', default='bi_lstm', type=str, action='store', help='The input file')
    parser.add_argument('--attention-layer', dest='attention_layer', default='False', action='store', type=str, help='The input file')
    #parser.add_argument('--optimizer', dest='input_length', default=100, action='store', type=int, help='The input file')
    #parser.add_argument('--loss', dest='input_length', default=100, action='store', type=int, help='The input file')
    args = parser.parse_args()
    
#Step 1- Passing the target_class to the class with name of morbidity_obj
    morbidity_obj = morbidity(args.target_class)
    print(args.target_class)
    print(args.word_embedding)
    print(args.model_type)

#Step 2- Applying the method/function texts_and_labels      (no arguments)
    morbidity_obj.texts_and_labels()

#Step 3- Appyling the method/function padded_encoded_text   (no arguments)
    morbidity_obj.padded_encoded_text()
    
#Step 4- Applying the method/function to choose the type of word embedding   (passing arguments)
    #morbidity_obj.build_embedding_matrix()
    if args.word_embedding == 'word2vec':  #dest is the variable and value after ==  which replaces the default value
        morbidity_obj.word2vec()
    elif args.word_embedding == 'glove':
        morbidity_obj.glove()
    elif args.word_embedding == 'fasttext':
        morbidity_obj.fasttext()
    elif args.word_embedding == 'domain':
        morbidity_obj.domain_train()
    elif args.word_embedding == 'bert':
        morbidity_obj.bert()
    else:
        print('Please use one of them: BERT, Word2Vec, Glove, Fasttext or Domain')
        exit(1)
    #sys.exit(1)
  
#Step 5- Applying the method/function train to run the model        
    if args.model_type == 'lstm':
        morbidity_obj.lstm()     #passing arguments inside the lstm to attention layer
    elif args.model_type == 'lstm_cnn':
        morbidity_obj.lstm_cnn()
    elif args.model_type == 'bi_lstm':
        morbidity_obj.bi_lstm()
    else:
        print('Please use one of models: lstm, lstm_cnn or bi_lstm')
        exit(1)
      
#Step 6- Applying the method/function train to run the model  
    #morbidity_obj.train()
    morbidity_obj.train(args.model_type, args.attention_layer)