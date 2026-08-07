# InventoryAccuracyModel
This Project predicts an inventory stock using lightgbm 
You will need a dataset with the following columns:
date,sku_id,brand,units_sold,restocked_units,recorded_stock,price

After you get these you can add it into explore.py in EDA folder which will show different graphs that plot key details like outliers, line graph, and also the top 10 highest sold sku's.

Then you can insert it into prepare_data.py in Training folder to add add some more features like promotional discount and it will also get the data into weekly_df which will help in understanding the trend of each sku. 
The daily and weekly processing datasets will be created.

train_model.py will train the data using LightGBM a gradient boosting machine that uses decision trees and the Mean Absolute Error will be created which will give us an average error of units. 
A safety stock is also added so that the sku's are not left to nill and some units are left if more are sold than expected. 

Dashboard.py is a streamlit app that gives us a small idea on how each sku_id is projected using the LightGBM Regressor and a naive baseline rolling_8w_mean both are compared.

Conclusion:
The lightgbm regressor did not perform so well and the naive baseline of rolling_8w_mean performed better with a lower MAE(Mean Absolute Error). New features added were lags of 1 week 2 week 4 week, rolling_4w_mean rolling_4w_std rolling_4w_median and a rolling_8w_mean.

Disclaimer: 
This was build on dummy data and if someone wants to use it they may test it by themselves. More work needs to be done on it.


