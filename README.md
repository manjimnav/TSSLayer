# Embedded temporal feature selection for time series forecasting using deep learning

Traditional time series forecasting models often use all available variables, including potentially irrelevant or noisy features, which can lead to overfitting and poor performance. Feature selection can help address this issue by selecting the most informative variables in the temporal and feature dimensions. However, selecting the right features can be challenging for time series models. Embedded feature selection has been a popular approach, but many techniques do not include it in their design, including deep learning methods, which can lead to less efficient and effective feature selection.
This article presents a deep learning-based method for time series forecasting that incorporates feature selection to improve model efficacy and interpretability. The proposed method uses a multidimensional layer to remove irrelevant features along the temporal dimension. The resulting model is compared to a baseline model that uses all available features, and experimental results demonstrate that the proposed approach can improve forecasting accuracy while reducing model complexity. Additionally, the selected features provide insights into the underlying patterns and drivers of the time series, aiding in the interpretation of the forecasting results.
Overall, the proposed method offers a simple and effective solution for time series forecasting with feature selection using deep learning techniques. This method can be used as a general-purpose approach for various applications and can potentially improve the accuracy and interpretability of time series forecasting models.

This repository includes all the code used for the development of this work. The data is available at the following link:

In order to use the repository, data must be stored in the `data/processed` folder and the results of the execution are stored in a csv in the `results` folder.

The repository includes two notebooks:

* experiment.ipynb: Includes the workflow to obtain the results of the experimentation.
* analysis.ipynb: Includes the tables used in the paper.
