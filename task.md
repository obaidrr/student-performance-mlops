## TASK ##
    - We need to build and End-to-End machine learning pipeling using airflow.
    - there are some steps that should be present in the machine learning pipeline.
    - I have created 6 dags in the airflow/dags folder.
        
        01. dataset_preprocessor_and_csv_to_mysql_dag.py should take the dataset present in the dataset/raw/StudentPerformanceFactors.csv and should perform all the preprocessing steps and should finally store the data into a mysql database.
        
        02. model_selector_dag.py should select relevent supravised machine learning mode it can be a regression model or a classification model and perform some tests to findout which models are the suitable for making meaningful predictions over the dataset. 

        03. model_training_dag.py should train the relevent model over the dataset it can be both regression model and the classification model. 

        04. model_tunner_dag.py should tune select the best performing model and perform so tunning to make the model performance better. 

        05. model_tester_dag.py should run some evaluation tests over the models and check everything is working fine and models are giving the right response. 

        06. finally model_extractor_dag.py should extract all the models as a joblib file and should store this in artifacts folder persent in the root directory. 

    - After the model is extracted to the artifacts folder we need to make relevent api-endpoints using Fastapi server in the api-server folder present over the root directory. 

    - Build a simple React frontend which includes a landing page and a make a prediction page and a model performance page. 

    - Add Dockerfiles to the airflow/dags, api-server and the frontend react application. And
    to run all the required services at once add all the required services in the docker-compose file. 
    
    - create a project-context.txt file where you should write the complete context of the project as detailed as possible. 
    