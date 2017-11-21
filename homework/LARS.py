from sklearn.linear_model import Lars
from homework import conf_hw
import numpy as np
import time

if __name__ == '__main__':
    fout = open('../data/predict_LARS.txt', 'wt', encoding='utf-8')
    total_error = 0
    for qid in range(201, 251):
        print(qid)
        time_in = time.time()
        qid = str(qid)
        X_train, Y_train = conf_hw.read_train(qid)
        X_test, Y_test = conf_hw.read_test(qid)
        y_train = np.array(Y_train).ravel()
        y_test = np.array(Y_test).ravel()

        model = Lars()
        model.fit(X_train, Y_train)
        y_hat = model.predict(X_test)

        i = 0
        for relationship in conf_hw.coll_test.find({'query_id': qid}):
            article_id = relationship['article_id']
            id_code = relationship['id_code']
            score = y_hat[i]
            fout.write(
                '{0} Q0 {1} {2} {3} Hiemstra_LM0.15_Bo1bfree_d_3_t_10\n'.format(qid, article_id, id_code, score))
            i += 1
        mae = sum(abs(y_hat-y_test)) / X_test.shape[0]
        print('time: {0}'.format(time.time()- time_in))
    print('avg mae: {0}'.format(total_error/50))