import numpy as np
#from homework import conf_hw
import conf_hw
from sklearn import tree as s_tree


class tree(object):
    def __init__(self, left=None, right=None, data=None):
        self.left = left
        self.right = right
        self.data = data


class DescisionTreeClassifier:
    def __init__(self):
        self.tree = None
        self.name = 'CART'
        self.nums = 0
        self.rows = None
        self.columns = None
        self.x_train = None
        self.y_train = None

    def gini(self, d):
        set_values = set(d)
        gini_value = 0
        len_d = float(len(d))
        for value in set_values:
            gini_value += (float(d.count(value))/len_d)**2
        return 1-gini_value

    def max_class(self, rows):
        y = list(self.y_train[rows])
        cls = 0
        if y.count(1) > y.count(0):
            cls = 1
        return cls

    def __fit(self, available_row, available_columns):
        available_row = available_row.copy()
        available_columns = available_columns.copy()

        if len(available_row) <= 0:
            raise Exception("rows or columns can't be empty")

        y_set = list(set(self.y_train[available_row]))
        # 叶子节点 --- 正常分类完成
        if len(y_set) == 1:
            print('class {0}'.format(y_set[0]))
            return tree(data={'class': y_set[0]})
        # 叶子节点 --- feature用完,采用投票制来确定class
        if len(available_columns) == 0:
            cls = self.max_class(available_row)
            print('no feature. class {0}'.format(cls))
            return tree(data={'class': cls})

        remove_feature = []
        best_gini = np.inf
        selected_feature = None
        selected_feature_value = None

        #  找feature和value使得gini(y |f, v) 最小
        for feature in available_columns:
            available_value = list(set(self.x_train[available_row, feature]))
            # 去除无区分度属性
            if len(available_value) < 2:
                remove_feature.append(feature)
                continue
            for value in available_value:
                d1 = []
                d2 = []
                for row in available_row:
                    if self.x_train[row, feature] == value:
                        d1.append(self.y_train[row])
                    else:
                        d2.append(self.y_train[row])
                    partition_gini = float(len(d1))/float(len(available_row)) * self.gini(d1) + \
                                     float(len(d2))/float(len(available_row)) * self.gini(d2)
                    if partition_gini <= best_gini:
                        best_gini = partition_gini
                        selected_feature = feature
                        selected_feature_value = value
        # 使用最优的feature 和 value对数据集进行分割
        if selected_feature == None:
            cls = self.max_class(available_row)
            print("all non't available feature. class {0}".format(cls))
            return tree(data={'class': cls})
        d1_row = []
        d2_row = []
        for row in available_row:
            if self.x_train[row, selected_feature] == selected_feature_value:
                d1_row.append(row)
            else:
                d2_row.append(row)
        # 去除相应的feature
        remove_feature.append(selected_feature)
        for rf in remove_feature:
            available_columns.remove(rf)

        node_data = dict()
        node_data['gini'] = best_gini
        node_data['feature'] = selected_feature
        node_data['value'] = selected_feature_value
        node_data['remove_feature'] = remove_feature
        left_chlid = self.__fit(d1_row, available_columns)
        right_child = self.__fit(d2_row, available_columns)
        return tree(left=left_chlid, right=right_child, data=node_data)

    def fit(self, x_train, y_train):
        self.x_train = x_train.copy()
        self.y_train = y_train.copy()
        self.rows, self.columns = x_train.shape
        self.tree = self.__fit(list(range(self.rows)), list(range(self.columns)))
        return tree

    def predict(self, x_test):
        y_hat = []
        row, column = x_test.shape
        for r in range(row):
            node = self.tree
            while True:
                if 'class' in node.data.keys():
                    y_hat.append(node.data['class'])
                    break
                else:
                    feature = node.data['feature']
                    feature_value = node.data['value']
                    if x_test[r, feature] == feature_value:
                        node = node.left
                    else:
                        node = node.right
        return y_hat


if __name__ == '__main__':
    alr = 'm5'
    print('start....')
    error_num = 0
    total_num = 0
    fout = open('../data/predict_{0}.txt'.format(alr), 'wt', encoding='utf-8')
    for qid in range(201, 251):
        x_train, y_train = conf_hw.read_train(qid, type='class')
        x_train = np.array(x_train)
        y_train = np.array(y_train).ravel()
        x_test, y_test = conf_hw.read_test(qid, type='class')
        x_test = np.array(x_test)
        y_test = np.array(y_test).ravel()
        clf = None
        if alr == 'cart':
            clf = DescisionTreeClassifier()
        elif alr == 'id3':
            clf = s_tree.DecisionTreeClassifier(criterion='entropy')
        elif alr == 'c4.5':
            clf = s_tree.DecisionTreeClassifier(criterion='entropy')
        elif alr == 'chaid':
            clf = s_tree.DecisionTreeClassifier(criterion='entropy')
        elif alr == 'm5':
            clf = s_tree.DecisionTreeClassifier(criterion='entropy')
        clf.fit(x_train, y_train)
        y_hat = clf.predict(x_test)
        # error ration
        for r in range(len(y_hat)):
            if y_hat[r] != y_test[r]:
                error_num += 1
        total_num += len(y_hat)

        # write file
        i = 0
        for relationship in conf_hw.coll_class_test.find({'query_id': str(qid)}):
            article_id = relationship['article_id']
            id_code = relationship['id_code']
            score = y_hat[i]
            fout.write(
                '{0} Q0 {1} {2} {3} Hiemstra_LM0.15_Bo1bfree_d_3_t_10\n'.format(qid, article_id, id_code, score))
            i += 1
    print('error_ration: {0}'.format(float(error_num)/float(total_num)))
    # error_ration: 0.2571127502634352
