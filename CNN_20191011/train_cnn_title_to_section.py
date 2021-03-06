# -*- coding:utf-8 -*-
import tensorflow as tf
import os
import pickle
import json
from tqdm import tqdm
from random import shuffle
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.backend as K
from collections import Counter
import re
import numpy as np
from tensorflow.keras import preprocessing
from tensorflow.keras.utils import plot_model
from tensorflow.keras import backend
# import spacy
# from spacy.tokenizer import Tokenizer
# from spacy.lang.en import English
# nlp = English()
# tokenizer = nlp.Defaults.create_tokenizer(nlp)
# en = spacy.load('en_core_web_sm')
# en.pipeline = [en.tagger, en.parser]

tf.compat.v1.enable_eager_execution

# data_path = '../data/Raw_Claim/'
# EMB_SIZE = 300
# RNG_SEED = 100   # 어제 실험한 것과 오늘 실험한게 일관성을 가지려면 초기값 고정 필요
# BATCH_SIZE = 8
# NUM_EPOCHS = 1

tf.keras.backend.clear_session()

# max_length = 10
# TEST_SPLIT = 0.7

raw_path = '../data/Raw_Claim'
tr_file_list = os.listdir(raw_path)
tr_file_list = [file for file in tr_file_list if file.endswith(".txt")]
# file_list = [file for file in file_list if file.endswith("docs.txt")]

test_data_path = '../data/Raw_Claim/test_data'
test_file_list = os.listdir(test_data_path)
test_file_list = [file for file in test_file_list if file.endswith(".txt")]


class Dataset:

    def __init__(self, train_path, test_path, is_shuffle, train_bs, test_bs, epoch, max_length, vocab_path, label_path):
        self.train_path = train_path
        self.test_path = test_path
        self.is_shuffle = is_shuffle
        self.train_bs = train_bs
        self.test_bs = test_bs
        self.epoch = epoch
        self.max_length = max_length
        # self.is_header_first = is_header_first
        # self.okt = Okt()
        self.special_tokens = ['<PAD>', '<BOS>', '<EOS>', '<UNK>']
        self.label_path = label_path
        self.vocab_path = vocab_path

        if not os.path.exists(self.vocab_path):
            print('No vocabulary.')
            print('Making vocabulary.')
            # self.build_vocab_by_patdata(vocab_path)
            self.build_vocab_by_patent(vocab_path)
            print('Complete build vocabulary!')

        # print('Loading vocabulary...')
        self.idx2word, self.word2idx = pickle.load(open(vocab_path, 'rb'))
        print('Successfully load vocabulary!')
        self.idx2label, self.label2idx = pickle.load(open(label_path, 'rb'))
        print('Successfully load labels')

    def build_freq(self, word_list):
        word_counts = Counter(word_list)
        # print('word_list: ', len(word_list), word_list)
        # print('word_counts_1: ', len(word_counts), word_counts)
        # print('word_counts_2: ', len(word_counts.most_common()), word_counts.most_common())
        freq = Counter()
        freq_file = raw_path + '/word_freq.pickle'
        # print(freq_file)
        if os.path.exists(freq_file):
            with open(freq_file, 'rb') as freq_dist_f:
                freq = pickle.load(freq_dist_f)
                print('frequency distribution loaded', len(freq), freq)
        for word, cnt in word_counts.items():
            # print(word, freq[word])
            freq[word] += cnt
            # print(word, freq[word])
        print('freq len: ', len(freq))
        with open(freq_file, 'wb') as freq_dist_f:
            pickle.dump(freq, freq_dist_f)
        return freq
    """
    word_list:  686 ['Adjustable', 'shoulder', 'device', 'for', 'hard', 'upper', 'torso', 'suit', 'A', 'suit', 'includes', 'a', 'hard', 'upper', 'torso', 'providing', 'shoulder', 'apertures.', 'A', 'repositionable', 'scye', 'bearing', 'is', 'arranged', 'at', 'a', 'shoulder', 'aperture.', 'An', 'adjustable', 'shoulder', 'device', 'interconnects', 'the', 'scye', 'bearing', 'and', 'the', 'hard', 'upper', 'torso.', 'The', 'adjustable', 'shoulder', 'device', 'is', 'configured', 'to', 'move', 'the', 'scye', 'bearing', 'between', 'first', 'and', 'second', 'shoulder', 'width', 'positions', 'relative', 'to', 'the', 'hard', 'upper', 'torso.', 'A', 'method', 'of', 'donning', 'a', 'suit', 'includes', 'the', 'steps', 'of', 'adjusting', 'a', 'scye', 'bearing', 'relative', 'to', 'a', 'hard', 'upper', 'torso', 'to', 'a', 'desired', 'shoulder', 'width', 'position.', 'The', 'scye', 'bearing', 'can', 'be', 'subsequently', 'repositioned', 'for', 'desired', 'crewmember', 'fit', 'and', 'use', 'while', 'the', 'desired', 'shoulder', 'width', 'position', 'is', 'maintained.', 'Eye', 'protectors', 'An', 'eye', 'protector', '(16)', 'is', 'provided', 'for', 'mounting', 'on', 'a', 'helmet', '(10)', 'of', 'the', 'type', 'worn', 'by', 'a', 'firefighter', 'or', 'other', 'emergency', 'worker,', 'the', 'helmet', 'having', 'a', 'brim', '(14)', 'that', 'projects', 'forwardly', 'and', 'laterally', 'from', 'a', 'lower', 'part', 'of', 'a', 'crown', '(12).', 'The', 'eye', 'protector', '(16)', 'includes', 'a', 'bracket', '(20)', 'mounted', 'to', 'the', 'brim', '(14),', 'a', 'pair', 'of', 'eye', 'shields', '(18)', 'movable', 'between', 'a', 'storage', 'position', 'extending', 'along', 'the', 'brim', '(14)', 'and', 'a', 'usage', 'position', 'extending', 'downward', 'from', 'the', 'brim', '(14)', 'to', 'shield', 'the', 'eyes', 'of', 'the', 'wearer,', 'and', 'a', 'pair', 'of', 'hinges', '(22)', 'to', 'connect', 'the', 'eye', 'shields', '(18)', 'to', 'the', 'bracket', '(20)', 'for', 'movement', 'between', 'the', 'storage', 'and', 'usage', 'positions.', 'Each', 'of', 'the', 'hinges', '(22)', 'connects', 'a', 'corresponding', 'one', 'of', 'the', 'eye', 'shields', '(18)', 'and', 'includes', 'a', 'plurality', 'of', 'aligned', 'hinge', 'openings', '(24,26)', 'on', 'the', 'eye', 'shield', '(18)', 'and', 'the', 'bracket', '(20),', 'a', 'socket', '(28)', 'on', 'the', 'eye', 'shield', '(18),', 'and', 'a', 'hinge', 'pin', '(30)', 'extending', 'through', 'the', 'hinge', 'openings', '(24,26)', 'and', 'have', 'a', 'first', 'end', '(32)', 'releasably', 'fixed', 'in', 'the', 'socket', '(28)', 'and', 'a', 'second', 'end', '(34)', 'that', 'is', 'exposed', 'outside', 'of', 'the', 'openings', '(24,26).', 'Combination', 'headgear', 'and', 'eye', 'protection', 'system', 'A', 'combination', 'headgear', 'assembly', 'and', 'protective', 'eyewear', 'system', 'includes', 'protective', 'eyewear', 'that', 'attaches', 'to', 'a', 'headgear', 'assembly', 'via', 'magnetic', 'connectors.', 'The', 'headgear', 'assembly', 'includes', 'an', 'adjustable', 'headrest', 'with', 'first', 'and', 'second', 'ends.', 'The', 'first', 'end', 'connects', 'to', 'a', 'first', 'spherical', 'capsule', 'having', 'a', 'first', 'side', 'wall,', 'and', 'the', 'second', 'end', 'connects', 'to', 'a', 'second', 'spherical', 'capsule', 'having', 'a', 'second', 'side', 'wall.', 'The', 'protective', 'eyewear', 'includes', 'a', 'vision', 'blade', 'with', 'a', 'first', 'end', 'attaching', 'via', 'a', 'first', 'finger', 'to', 'a', 'first', 'telescoping', 'member', 'while', 'a', 'second', 'end', 'attaches', 'via', 'a', 'second', 'finger', 'to', 'a', 'second', 'telescoping', 'member.', 'A', 'first', 'magnetic', 'connector', 'is', 'positioned', 'between', 'the', 'first', 'telescoping', 'member', 'and', 'the', 'first', 'side', 'wall', 'of', 'the', 'first', 'spherical', 'capsule,', 'and', 'a', 'second', 'magnetic', 'connector', 'is', 'positioned', 'between', 'the', 'first', 'telescoping', 'member', 'and', 'the', 'second', 'side', 'wall', 'of', 'the', 'second', 'spherical', 'capsule.', 'Garment', 'protective', 'assembly', 'A', 'garment', 'such', 'as', 'a', 'shirt', 'or', 'pants', 'has', 'a', 'front', 'layer', 'with', 'portions', 'which', 'define', 'a', 'central', 'opening', 'defined', 'by', 'an', 'inner', 'periphery', 'and', 'positionable', 'to', 'overlie', 'a', 'portion', 'of', 'the', 'joint', 'to', 'be', 'protected', 'such', 'as', 'a', 'knee', 'or', 'an', 'elbow.', 'A', 'removable', 'protective', 'insert', 'is', 'larger', 'than', 'the', 'central', 'opening', 'and', 'has', 'a', 'unitary', 'cap', 'sewn', 'thereto.', 'The', 'cap', 'has', 'an', 'upper', 'segment', 'separated', 'from', 'a', 'lower', 'segment', 'by', 'a', 'bending', 'joint', 'defined', 'by', 'at', 'least', 'one', 'groove', 'which', 'extends', 'substantially', 'across', 'the', 'cap.', 'The', 'upper', 'segment', 'and', 'the', 'lower', 'segment', 'are', 'separately', 'fixed', 'to', 'the', 'protective', 'insert', 'by', 'stitching.', 'The', 'upper', 'segment', 'and', 'the', 'lower', 'segment', 'have', 'an', 'outwardly', 'projecting', 'flange', 'which', 'overlies', 'the', 'protective', 'insert,', 'the', 'flange', 'having', 'portions', 'which', 'engage', 'the', 'front', 'layer', 'of', 'the', 'garment', 'between', 'the', 'cap', 'flange', 'and', 'the', 'protective', 'insert.', 'A', 'slot', 'in', 'the', 'insert', 'ventilates', 'through', 'the', 'front', 'layer.', 'Visored', 'cloth', 'headgear', 'An', 'item', 'of', 'headgear', 'comprised', 'of', 'a', 'visor', 'bill', 'attached', 'to', 'a', 'square', 'piece', 'of', 'cloth', 'along', 'the', 'diagonal', 'of', 'the', 'cloth', 'and', 'slightly', 'below', 'the', 'center', 'of', 'the', 'cloth.', 'The', 'visor', 'bill', 'is', 'encased', 'in', 'a', 'pocket-shaped', 'visor', 'bill', 'cover', 'before', 'it', 'is', 'stitched', 'to', 'the', 'square', 'piece', 'of', 'cloth.', 'The', 'present', 'invention', 'can', 'be', 'worn', 'as', 'a', 'visor,', 'or', 'it', 'can', 'be', 'opened', 'up', 'and', 'wrapped', 'over', 'the', 'top', 'of', 'the', 'head', 'to', 'form', 'the', 'shape', 'of', 'a', 'more', 'traditional', 'hat.']
    word_counts_1:  251 Counter({'the': 53, 'a': 48, 'and': 26, 'of': 23, 'to': 19, 'first': 14, 'second': 12, 'The': 11, 'is': 10, 'shoulder': 8, 'upper': 8, 'A': 8, 'eye': 8, 'protective': 8, 'includes': 7, 'between': 6, 'end': 6, 'headgear': 6, 'segment': 6, 'hard': 5, 'scye': 5, 'bearing': 5, 'by': 5, 'an': 5, 'for': 4, 'be': 4, 'or': 4, 'having': 4, 'brim': 4, 'lower': 4, '(18)': 4, 'assembly': 4, 'spherical': 4, 'side': 4, 'telescoping': 4, 'which': 4, 'device': 3, 'torso': 3, 'suit': 3, 'An': 3, 'adjustable': 3, 'width': 3, 'desired': 3, 'can': 3, 'position': 3, 'on': 3, '(14)': 3, 'that': 3, 'from': 3, 'bracket': 3, 'shields': 3, 'extending': 3, 'shield': 3, 'connects': 3, 'hinge': 3, 'openings': 3, 'in': 3, 'eyewear': 3, 'via': 3, 'magnetic': 3, 'with': 3, 'member': 3, 'as': 3, 'has': 3, 'front': 3, 'insert': 3, 'cap': 3, 'flange': 3, 'cloth': 3, 'visor': 3, 'bill': 3, 'at': 2, 'torso.': 2, 'relative': 2, 'while': 2, 'protector': 2, '(16)': 2, 'helmet': 2, 'worn': 2, '(20)': 2, 'pair': 2, 'storage': 2, 'along': 2, 'usage': 2, 'hinges': 2, '(22)': 2, 'one': 2, '(24,26)': 2, 'socket': 2, '(28)': 2, 'through': 2, 'have': 2, 'fixed': 2, 'system': 2, 'attaches': 2, 'capsule': 2, 'finger': 2, 'connector': 2, 'positioned': 2, 'wall': 2, 'garment': 2, 'such': 2, 'layer': 2, 'portions': 2, 'central': 2, 'opening': 2, 'defined': 2, 'joint': 2, 'square': 2, 'piece': 2, 'cloth.': 2, 'it': 2, 'Adjustable': 1, 'providing': 1, 'apertures.': 1, 'repositionable': 1, 'arranged': 1, 'aperture.': 1, 'interconnects': 1, 'configured': 1, 'move': 1, 'positions': 1, 'method': 1, 'donning': 1, 'steps': 1, 'adjusting': 1, 'position.': 1, 'subsequently': 1, 'repositioned': 1, 'crewmember': 1, 'fit': 1, 'use': 1, 'maintained.': 1, 'Eye': 1, 'protectors': 1, 'provided': 1, 'mounting': 1, '(10)': 1, 'type': 1, 'firefighter': 1, 'other': 1, 'emergency': 1, 'worker,': 1, 'projects': 1, 'forwardly': 1, 'laterally': 1, 'part': 1, 'crown': 1, '(12).': 1, 'mounted': 1, '(14),': 1, 'movable': 1, 'downward': 1, 'eyes': 1, 'wearer,': 1, 'connect': 1, 'movement': 1, 'positions.': 1, 'Each': 1, 'corresponding': 1, 'plurality': 1, 'aligned': 1, '(20),': 1, '(18),': 1, 'pin': 1, '(30)': 1, '(32)': 1, 'releasably': 1, '(34)': 1, 'exposed': 1, 'outside': 1, '(24,26).': 1, 'Combination': 1, 'protection': 1, 'combination': 1, 'connectors.': 1, 'headrest': 1, 'ends.': 1, 'wall,': 1, 'wall.': 1, 'vision': 1, 'blade': 1, 'attaching': 1, 'member.': 1, 'capsule,': 1, 'capsule.': 1, 'Garment': 1, 'shirt': 1, 'pants': 1, 'define': 1, 'inner': 1, 'periphery': 1, 'positionable': 1, 'overlie': 1, 'portion': 1, 'protected': 1, 'knee': 1, 'elbow.': 1, 'removable': 1, 'larger': 1, 'than': 1, 'unitary': 1, 'sewn': 1, 'thereto.': 1, 'separated': 1, 'bending': 1, 'least': 1, 'groove': 1, 'extends': 1, 'substantially': 1, 'across': 1, 'cap.': 1, 'are': 1, 'separately': 1, 'stitching.': 1, 'outwardly': 1, 'projecting': 1, 'overlies': 1, 'insert,': 1, 'engage': 1, 'insert.': 1, 'slot': 1, 'ventilates': 1, 'layer.': 1, 'Visored': 1, 'item': 1, 'comprised': 1, 'attached': 1, 'diagonal': 1, 'slightly': 1, 'below': 1, 'center': 1, 'encased': 1, 'pocket-shaped': 1, 'cover': 1, 'before': 1, 'stitched': 1, 'present': 1, 'invention': 1, 'visor,': 1, 'opened': 1, 'up': 1, 'wrapped': 1, 'over': 1, 'top': 1, 'head': 1, 'form': 1, 'shape': 1, 'more': 1, 'traditional': 1, 'hat.': 1})
    word_counts_2:  251 [('the', 53), ('a', 48), ('and', 26), ('of', 23), ('to', 19), ('first', 14), ('second', 12), ('The', 11), ('is', 10), ('shoulder', 8), ('upper', 8), ('A', 8), ('eye', 8), ('protective', 8), ('includes', 7), ('between', 6), ('end', 6), ('headgear', 6), ('segment', 6), ('hard', 5), ('scye', 5), ('bearing', 5), ('by', 5), ('an', 5), ('for', 4), ('be', 4), ('or', 4), ('having', 4), ('brim', 4), ('lower', 4), ('(18)', 4), ('assembly', 4), ('spherical', 4), ('side', 4), ('telescoping', 4), ('which', 4), ('device', 3), ('torso', 3), ('suit', 3), ('An', 3), ('adjustable', 3), ('width', 3), ('desired', 3), ('can', 3), ('position', 3), ('on', 3), ('(14)', 3), ('that', 3), ('from', 3), ('bracket', 3), ('shields', 3), ('extending', 3), ('shield', 3), ('connects', 3), ('hinge', 3), ('openings', 3), ('in', 3), ('eyewear', 3), ('via', 3), ('magnetic', 3), ('with', 3), ('member', 3), ('as', 3), ('has', 3), ('front', 3), ('insert', 3), ('cap', 3), ('flange', 3), ('cloth', 3), ('visor', 3), ('bill', 3), ('at', 2), ('torso.', 2), ('relative', 2), ('while', 2), ('protector', 2), ('(16)', 2), ('helmet', 2), ('worn', 2), ('(20)', 2), ('pair', 2), ('storage', 2), ('along', 2), ('usage', 2), ('hinges', 2), ('(22)', 2), ('one', 2), ('(24,26)', 2), ('socket', 2), ('(28)', 2), ('through', 2), ('have', 2), ('fixed', 2), ('system', 2), ('attaches', 2), ('capsule', 2), ('finger', 2), ('connector', 2), ('positioned', 2), ('wall', 2), ('garment', 2), ('such', 2), ('layer', 2), ('portions', 2), ('central', 2), ('opening', 2), ('defined', 2), ('joint', 2), ('square', 2), ('piece', 2), ('cloth.', 2), ('it', 2), ('Adjustable', 1), ('providing', 1), ('apertures.', 1), ('repositionable', 1), ('arranged', 1), ('aperture.', 1), ('interconnects', 1), ('configured', 1), ('move', 1), ('positions', 1), ('method', 1), ('donning', 1), ('steps', 1), ('adjusting', 1), ('position.', 1), ('subsequently', 1), ('repositioned', 1), ('crewmember', 1), ('fit', 1), ('use', 1), ('maintained.', 1), ('Eye', 1), ('protectors', 1), ('provided', 1), ('mounting', 1), ('(10)', 1), ('type', 1), ('firefighter', 1), ('other', 1), ('emergency', 1), ('worker,', 1), ('projects', 1), ('forwardly', 1), ('laterally', 1), ('part', 1), ('crown', 1), ('(12).', 1), ('mounted', 1), ('(14),', 1), ('movable', 1), ('downward', 1), ('eyes', 1), ('wearer,', 1), ('connect', 1), ('movement', 1), ('positions.', 1), ('Each', 1), ('corresponding', 1), ('plurality', 1), ('aligned', 1), ('(20),', 1), ('(18),', 1), ('pin', 1), ('(30)', 1), ('(32)', 1), ('releasably', 1), ('(34)', 1), ('exposed', 1), ('outside', 1), ('(24,26).', 1), ('Combination', 1), ('protection', 1), ('combination', 1), ('connectors.', 1), ('headrest', 1), ('ends.', 1), ('wall,', 1), ('wall.', 1), ('vision', 1), ('blade', 1), ('attaching', 1), ('member.', 1), ('capsule,', 1), ('capsule.', 1), ('Garment', 1), ('shirt', 1), ('pants', 1), ('define', 1), ('inner', 1), ('periphery', 1), ('positionable', 1), ('overlie', 1), ('portion', 1), ('protected', 1), ('knee', 1), ('elbow.', 1), ('removable', 1), ('larger', 1), ('than', 1), ('unitary', 1), ('sewn', 1), ('thereto.', 1), ('separated', 1), ('bending', 1), ('least', 1), ('groove', 1), ('extends', 1), ('substantially', 1), ('across', 1), ('cap.', 1), ('are', 1), ('separately', 1), ('stitching.', 1), ('outwardly', 1), ('projecting', 1), ('overlies', 1), ('insert,', 1), ('engage', 1), ('insert.', 1), ('slot', 1), ('ventilates', 1), ('layer.', 1), ('Visored', 1), ('item', 1), ('comprised', 1), ('attached', 1), ('diagonal', 1), ('slightly', 1), ('below', 1), ('center', 1), ('encased', 1), ('pocket-shaped', 1), ('cover', 1), ('before', 1), ('stitched', 1), ('present', 1), ('invention', 1), ('visor,', 1), ('opened', 1), ('up', 1), ('wrapped', 1), ('over', 1), ('top', 1), ('head', 1), ('form', 1), ('shape', 1), ('more', 1), ('traditional', 1), ('hat.', 1)]
    """

    def build_vocab_by_patent(self, vocab_path):
        error_cnt = 0
        label_list = []
        for file in self.train_path:
            word_list = []
            with open(os.path.join(raw_path, file), encoding='utf-8') as f:
                for line in tqdm(f):
                    try:
                        # print('line: ', line)
                        patent = json.loads(line)
                        text = re.sub('[-=.#/?:$}(){,]', ' ', patent['title'] + patent['ab'])
                        token = text.split()
                        # token = tokenizer(patent['title'])
                        # print('token: ', token)
                        # doc = en.tokenizer(patent['title']+patent['ab']+patent['cl'])
                        labels = patent['cpc'].split('|')
                        for tok in token:
                            word_list.append(tok.lower())
                        labels = [label[0] for label in labels]
                        for label in labels:
                            if label not in label_list:
                                label_list.append(label)
                    except:
                        error_cnt += 1
                        # print('error: ', line)
            print('\nIn "%s" word_list: %d, error_cnt: %d\n' % (file, len(word_list), error_cnt))
            # idx2word, word2idx = self.build_freq(word_list)
            idx2word = self.build_freq(word_list)
            # idx2label = self.build_labels(label_list)
            # print('idx2word: ', len(idx2word), idx2word[:10])
        idx2word = self.special_tokens + [word for word, _ in idx2word.most_common()]
        print('idx2word: ', len(idx2word), idx2word[:10])
        print('idx2label: ', len(label_list), label_list)
        word2idx = {word: idx for idx, word in enumerate(idx2word)}
        label2idx = {label: idx for idx, label in enumerate(label_list)}
        vocab = (idx2word, word2idx)
        label = (label_list, label2idx)
        pickle.dump(vocab, open(vocab_path, 'wb'))
        pickle.dump(label, open(self.label_path, 'wb'))

    # def build_vocab(self, word_list):
    #     from collections import Counter
    #     word_counts = Counter(word_list)
    #     idx2word = self.special_tokens + [word for word, _ in word_counts.most_common()]
    #     word2idx = {word: idx for idx, word in enumerate(idx2word)}
    #     return idx2word, word2idx

    # def build_labels(self, label_list):
    #     label_file = raw_path + '/labels.pickle'
    #     if os.path.exists(label_file):
    #         with open(label_file, 'rb') as label_f:
    #             labels = pickle.load(label_f)
    #             print('saved label loaded', len(labels), labels)
    #     else:
    #         labels = []
    #
    #     for label in label_list:
    #         if label not in labels:
    #             labels.append(label)
    #             need_save = True
    #     print('labels: ', len(labels), labels)
    #     if need_save:
    #         with open(label_file, 'wb') as label_f:
    #             pickle.dump(label_file, label_f)
    #     return labels

    # def read_patents(self, file):
    #     with open(os.path.join(raw_path, file), encoding='utf-8') as f:
    #         for line in f:
    #             yield json.loads(line)
    #         # yield json.loads()

    # def build_vocab_by_patdata(self, vocab_path):
    #     for file in self.train_path:
    #         print('current file: ', file)
    #         with open(os.path.join(raw_path, file), encoding='utf-8') as f:  # 일단 읽어서 길이는 알아둔다.
    #             # data_length = len(f.readlines())
    #             # print(data_length)
    #             # for patent in patents:
    #             #     print(patent)
    #             #     # id_kipi, pd, cpc, title, ab, cl = f.read()
    #             #     print(patent('title'))
    #             #     tokenized_title = [patent['title'].split()]
    #             #     idx2word, word2idx = self.build_vocab(tokenized_title)
    #             #     vocab = (idx2word, word2idx)
    #             #     pickle.dump(vocab, open(vocab_path, 'wb'))
    #             for line in f:
    #                 try:
    #                     patent = json.loads(line)
    #                     print(patent['title'])
    #                     tokenized_title = en.tokenizer(patent['title'])
    #                     tokenized_ab = en.tokenizer(patent['ab'])
    #                     tokenized_cl = en.tokenizer(patent['cl'])
    #                     print('tokenized_title: ', tokenized_title)
    #                     print('tokenized_ab: ', tokenized_ab)
    #                     print('tokenized_cl: ', tokenized_cl)
    #                     # idx2word, word2idx = self.build_vocab(tokenized_title)
    #                     # vocab = (idx2word, word2idx)
    #                     # pickle.dump(vocab, open(vocab_path, 'wb'))
    #                 except:
    #                     pass

    # def tokenize_by_morph(self, text):
    #     tokenized_text = []
    #     for sentence in text:
    #         tokenized_text.append(self.okt.morphs(sentence))
    #     return tokenized_text

    def text_to_sequence(self, text_list):
        sequences = []
        for text in text_list:
            sequences.append([self.word2idx[word] for word in text if word in self.word2idx.keys()])
        return sequences

    def sequence_to_text(self, sequence):
        return [self.idx2word[idx] for idx in sequence if idx != 0]

    # def make_decoder_input_and_label(self, answers):
    #     decoder_input = []
    #     labels = []
    #     for sentence in answers:
    #         decoder_input.append(['<BOS>'] + sentence)
    #         labels.append(sentence + ['<EOS>'])
    #     return decoder_input, labels

    def read_lines(self, indices, path):
        line_count = 0
        texts = []
        labels = []

        with open(path, encoding='utf-8') as f:
            for line in f:
                if line_count in indices:
                    try:
                        patent = json.loads(line)
                        text = re.sub('[-=.#/?:$}(){,]', ' ', patent['title'] + patent['ab'])
                        label = patent['cpc'].split('|')
                        texts.append(text.lower().split())
                        labels.append(list(set([cpc[0] for cpc in label])))
                    except:
                        print(line)
                        print(line_count)
                line_count += 1
        # print('texts: \n', len(texts), texts[:5])
        # print('\nlabels: \n', len(labels), labels)
        # print('\n')
        return texts, labels

    def create_multiplehot_labels(self, labels_index):
        labels = []
        # print(len(label))
        for batch in labels_index:
            label = [0] * len(self.label2idx)
            # print(item)
            for cpc in batch:
                label[self.label2idx[cpc]] = 1
            labels.append(label)
        # print('label_repr: ', labels)
        return labels

    def data_generator(self, is_train):
        if is_train:
            batch_size = self.train_bs
            is_shuffle = self.is_shuffle  # 셔플을 여기서 해줘야해. 밖에서는 느려
            file_list = tr_file_list
            # path = self.train_path
        else:
            batch_size = self.test_bs
            is_shuffle = False
            file_list = ['test_data/' + file for file in test_file_list]
            # path = self.test_path

        # file_list = [file for file in file_list if file.endswith("docs.txt")]
        # print(file_list)
        # for file in tqdm(shuffle(file_list)):
        for file in tqdm(file_list):
            cur_file = os.path.join(raw_path, file)
            with open(cur_file, encoding='utf-8') as f:  # 일단 읽어서 길이는 알아둔다.
                data_length = len(f.readlines())
                # print('Num of pat: ', data_length)

            indices = list(range(data_length))  # 인덱스를 미리 만들어주는게 제너레이터 사용의 핵심.
            if is_shuffle:
                shuffle(indices)  # 셔플할꺼라면 이걸... 내장 라이브러리 random에 있는 함수.

            current_count = 0
            while True:
                if current_count >= data_length:
                    return
                else:
                    target_indices = indices[current_count:current_count + batch_size]
                    texts, labels = self.read_lines(target_indices, cur_file)
                    # tokenized_title = self.tokenize_by_morph(title)
                    # tokenized_title = texts.split()
                    tokenized_title = texts
                    labels = self.create_multiplehot_labels(labels)
                    indexed_encoder_inputs = self.text_to_sequence(tokenized_title)
                    padded_encoder_inputs = pad_sequences(indexed_encoder_inputs,
                                                          maxlen=self.max_length,
                                                          padding='pre')
                    yield padded_encoder_inputs, labels

    def mapping_fn(self, x, y=None):
        inputs, label = {'x': x}, y
        return inputs, label

    def train_input_fn(self):
        dataset = tf.data.Dataset.from_generator(generator=lambda: self.data_generator(is_train=True),
                                                 output_types=(tf.int64, tf.int64),
                                                 output_shapes=(
                                                     (None, self.max_length),  # 넣어주면 graph그릴때 잘못 들어온 입력을 잡아줄 수 있다.
                                                     (None, None)))  # labels count: unknown
        # id_kipi, pd, cpc, title, ab, cl
        # for text, label in dataset.take(2):
        #     text = _print_function(text)
        #     print('value: ', text, label)
        dataset = dataset.map(self.mapping_fn)
        dataset = dataset.repeat(count=self.epoch)
        return dataset

    def test_input_fn(self):
        dataset = tf.data.Dataset.from_generator(generator=lambda: self.data_generator(is_train=False),
                                                 output_types=(tf.int64, tf.int64),
                                                 output_shapes=((None, self.max_length),
                                                                (None, None)))
        dataset = dataset.map(self.mapping_fn)
        return dataset

    def eval_input_fn(self):
        dataset = tf.data.Dataset.from_generator(generator=lambda: self.data_generator(is_train=False),
                                                 output_types=(tf.int64, tf.int64),
                                                 output_shapes=((None, self.max_length), (None, None)))
        # dataset = tf.data.Dataset.from_generator(generator=lambda: self.data_generator(is_train=False))
        dataset = dataset.map(self.mapping_fn)
        return dataset


vocab_path = os.path.join(raw_path + '/vocab.voc')
label_file = raw_path + '/labels.pickle'

dataset = Dataset(train_path=tr_file_list,
                  test_path=test_file_list,
                  is_shuffle=True,
                  train_bs=16,
                  test_bs=128,
                  epoch=10,
                  max_length=30,
                  vocab_path=vocab_path,
                  label_path=label_file
                  # is_header_first=True
                  )

# vocab_size = len(dataset.word2idx)
# print('vocab_size: ', vocab_size)


def model_fn(features, labels, mode, params):
    TRAIN = mode == tf.estimator.ModeKeys.TRAIN
    EVAL = mode == tf.estimator.ModeKeys.EVAL
    PREDICT = mode == tf.estimator.ModeKeys.PREDICT
    # feature['x'] => (bs, 20)

    """
    print('features: ', features)
    print('labels: ', labels)
    features:  {'x': <tf.Tensor 'IteratorGetNext:0' shape=(?, 30) dtype=int64>}
    labels:  Tensor("IteratorGetNext:1", shape=(?, ?), dtype=int64)
    """
    train_op = features
    loss = features
    predicted_token = features
    embedding_layer = tf.keras.layers.Embedding(params['vocab_size'],
                                                params['embedding_dimension'])(features['x'])  # (bs, 20, EMD_SIZE)

    # K.print_tensor(embedding_layer, message='Embedding Layer')
    # embedding = K.print_tensor(embedding_layer, message='Embedding Layer')
    # print('embedding: ', embedding)
    # embedding:  Tensor("Identity:0", shape=(?, 30, 128), dtype=float32)

    dropout_emb = tf.keras.layers.Dropout(rate=0.5)(embedding_layer)  # (bs, 20, EMD_SIZE)

    filter_sizes = [3, 4, 5]
    pooled_outputs = []
    for filter_size in filter_sizes:
        conv = tf.keras.layers.Conv1D(
            filters=100,
            kernel_size=filter_size,
            padding='valid',
            activation=tf.nn.relu,
            kernel_constraint=tf.keras.constraints.max_norm(3.))(dropout_emb)  # (bs, 20, 100)
        # 최대 norm 지정, weight clipping이 바로 이 부분

        pool = tf.keras.layers.GlobalMaxPool1D()(conv)  # [(bs, 100), (bs, 100), (bs, 100)]
        pooled_outputs.append(pool)

    h_pool = tf.concat(pooled_outputs, axis=1)  # (bs, 300)

    hidden = tf.keras.layers.Dense(units=250, activation=tf.nn.relu,
                                   kernel_constraint=tf.keras.constraints.max_norm(3.))(h_pool)  # (bs, 200)
    dropout_hidden = tf.keras.layers.Dropout(rate=0.5)(hidden, training=TRAIN)
    # logits = tf.keras.layers.Dense(units=1)(dropout_hidden)  # sigmoid를 해주겠다  # (bs, 1)
    logits = tf.keras.layers.Dense(units=params['label_size'])(dropout_hidden)  # 이렇게하면 one-hot 필요

    # if labels is not None:
    #     # labels = tf.reshape(labels, [-1, 1])  # (bs, 1)
    #     print('labels: ', labels)
    #     labels = tf.one_hot(indices=labels, depth=params['label_size'])  # (bs, 2)
    #     print('labels one_hot: ', labels)

    if TRAIN:
        global_step = tf.train.get_global_step()
        loss = tf.losses.sigmoid_cross_entropy(labels, logits,
                                               # weights=1.0, label_smoothing=0.01
                                               )
        # loss = tf.losses.softmax_cross_entropy(labels, logits)

        train_op = tf.train.AdamOptimizer(0.001).minimize(loss, global_step)

        return tf.estimator.EstimatorSpec(mode=mode, train_op=train_op, loss=loss)

    elif EVAL:
        loss = tf.losses.sigmoid_cross_entropy(labels, logits,
                                               weights=1.0, label_smoothing=0.01)
        pred = tf.nn.sigmoid(logits)
        accuracy = tf.metrics.accuracy(labels, tf.round(pred))
        top_k = tf.metrics.precision_at_top_k(labels=labels, predictions_idx=pred, k=2)
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops={'acc': accuracy,
                                                                                 'top-k': top_k})

    elif PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions={
                'prob': tf.nn.sigmoid(logits),
            }
        )
    # plot_model(model, to_file='model.png')

    return tf.estimator.EstimatorSpec(
        mode=mode,
        train_op=train_op,
        loss=loss,
        predictions={'prediction': predicted_token})


tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

hyper_params = {'vocab_size': len(dataset.word2idx),
                'label_size': len(dataset.label2idx),
                'embedding_dimension': 128,
                # 'gru_dimension': 128,
                # 'attention_dimension': 256,
                # 'start_token_index': dataset.word2idx['<BOS>'],
                'max_length': 30,
                'teacher_forcing_rate': 0.5,
                'use_attention': True}


est = tf.estimator.Estimator(model_fn=model_fn,
                             params=hyper_params,
                             model_dir="abst_to_section/checkpoint")

# est.train(dataset.train_input_fn)
valid = est.evaluate(dataset.eval_input_fn)
pred_results = est.predict(input_fn=dataset.eval_input_fn)
print(pred_results)
