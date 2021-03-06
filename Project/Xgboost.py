# -*- coding: utf-8 -*-

import os
os.environ["CUDA_VISIBLE_DEVICES"]='1' 
import time
import sys
import gc
import pickle
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from xgboost import plot_importance
import matplotlib.pyplot as plt
%matplotlib inline

items = pd.read_csv('data/items.csv')
shops = pd.read_csv('data/shops.csv')
cats = pd.read_csv('data/item_categories.csv')
train = pd.read_csv('data/sales_train.csv.gz',compression='gzip')
test  = pd.read_csv('data/test.csv.gz',compression='gzip').set_index('ID')

data = pd.read_pickle('data-all-features.pkl')

print(data.columns) # all features

# select features
data = data[['date_block_num', 'shop_id', 'item_id', 'item_cnt_month', 'city_code',
       'item_category_id', 'type_code', 'subtype_code', 
        'item_cnt_month_lag_1',
        'item_cnt_month_lag_2', 
        'item_cnt_month_lag_3', 
        'item_cnt_month_lag_6',
        'item_cnt_month_lag_12', 
        'date_avg_item_cnt_lag_1',
        'date_item_avg_item_cnt_lag_1', 
        'date_item_avg_item_cnt_lag_2',
        'date_item_avg_item_cnt_lag_3', 
        'date_item_avg_item_cnt_lag_6',
        'date_item_avg_item_cnt_lag_12', 
        'date_shop_avg_item_cnt_lag_1',
        'date_shop_avg_item_cnt_lag_2', 
        'date_shop_avg_item_cnt_lag_3',
        'date_shop_avg_item_cnt_lag_6', 
        'date_shop_avg_item_cnt_lag_12',
        'date_cat_avg_item_cnt_lag_1', 
        'date_cat_avg_item_cnt_lag_2',
        'date_cat_avg_item_cnt_lag_3', 
        'date_cat_avg_item_cnt_lag_6',
        'date_cat_avg_item_cnt_lag_12', 
        'date_shop_cat_avg_item_cnt_lag_1',
        'date_shop_cat_avg_item_cnt_lag_6', 
        'date_shop_type_avg_item_cnt_lag_1',
        'date_shop_type_avg_item_cnt_lag_6',
        'date_shop_subtype_avg_item_cnt_lag_1',
        'date_shop_subtype_avg_item_cnt_lag_6',
        'date_city_avg_item_cnt_lag_1',
        'date_city_avg_item_cnt_lag_6', 
        'date_item_city_avg_item_cnt_lag_1',
        'date_item_city_avg_item_cnt_lag_6',
        'date_type_avg_item_cnt_lag_1',
        'date_type_avg_item_cnt_lag_6', 
        'date_subtype_avg_item_cnt_lag_1', 
        'date_subtype_avg_item_cnt_lag_6',
       'delta_price_lag',
       'delta_revenue_lag_1', 'month', 'days', 'item_shop_last_sale',
       'item_shop_first_sale', 'item_first_sale', 'item_last_sale']]


X_train = data[data.date_block_num < 33].drop(['item_cnt_month'], axis=1)
Y_train = data[data.date_block_num < 33]['item_cnt_month']
X_valid = data[data.date_block_num == 33].drop(['item_cnt_month'], axis=1)
Y_valid = data[data.date_block_num == 33]['item_cnt_month']
X_test = data[data.date_block_num == 34].drop(['item_cnt_month'], axis=1)

del data
gc.collect();

# init model
model = XGBRegressor(
    max_depth=8,
    n_estimators=1000,
    min_child_weight=300, 
    subsample=0.8, 
    colsample_bytree=0.8, 
    eta=0.3,    
    seed=42)

# training
hist = model.fit(
    X_train, Y_train, 
    eval_metric="rmse", 
    eval_set=[(X_train, Y_train), (X_valid, Y_valid)], 
    verbose=True, 
    early_stopping_rounds = 10)

# plot curve
results = model.evals_result()
epochs = len(results['validation_0']['rmse'])
x_axis = range(0, epochs)

plt.figure()
fig, ax = plt.subplots()
ax.plot(x_axis, results['validation_0']['rmse'], 'bo',label='Train')
ax.plot(x_axis, results['validation_1']['rmse'], 'b-', label='Validation')
ax.legend()
plt.ylabel('RMSE')
plt.ylabel('Epochs')
plt.title('XGBoost RMSE')
plt.savefig("XGBoost_RMSE.png", dpi=150)
plt.show()

# predict on test set
Y_test = model.predict(X_test).clip(0, 20)

# save submission file
submission = pd.DataFrame({"ID": test.index,  "item_cnt_month": Y_test})
submission.to_csv('xgboost_submission.csv', index=False)
