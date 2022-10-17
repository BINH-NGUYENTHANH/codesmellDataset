## Authors: 
Nguyen Thanh Binh, Minh N. H. Nguyen, Le Thi My Hanh, and Nguyen Thanh Binh.
## Title: 
ml-Codesmell: A code smell prediction dataset for machine learning approaches. In Proceedings of The 11th International Symposium On Information And Communication Technology (SOICT ’2022).
## What does the project do?
This project proposes the ml-Codesmell dataset created by analysing source code and extracting massive source code metrics with many labelled code smells and has been used to train and predict code smell using machine learning algorithms. The proposed dataset is expected to be useful for research projects on predicting code smell based on a machine-learning approach.

The dataset includes two following folders:
### The ml-codesmell folder
This folder stores 2 data of the project as follows: 
The file project_catalogue.csv contains links to the open-source code project catalogue. The source code of projects in the catalogue is cloned and downloaded into local storage to analyse and extract source code metrics.
The ml-codesmell dataset is zipped and split into three files as ml-codesmell.zip, ml-codesmell.z01, and ml-codesmell.z02. Please unzip the file ml-codesmell.zip when using it.
### The python-code folder
This folder contains two following files:
1. File ml-codesmell.py is the python source code to evaluate the reliability of Brain Class labelled code smell samples in the class-level dataset based on machine learning algorithms. Other code smell in class-level and method-level datasets are evaluated similar
2. File ml_Codesmell_predictive_results.xlsx is the predictive results of all code smell in the ml_Codesmell dataset.

If you have any questions or problems using the dataset, please contact support over email: thanhbinh@cdtb.edu.vn.
