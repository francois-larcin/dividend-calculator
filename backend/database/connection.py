import psycopg2
from typing import Dict
import traceback
import logging

class DatabaseConnection:
    """"Connection Manager for PostgreSQL connections
    
    Automatically manage:
    - Connection openings
    - Successfull commits
    - Rollback if error
    - Connection closing
    """
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None #Created in __enter__

    
    def __enter__(self):
        self.connection = psycopg2.connect(**self.db_config)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is None:
                #No error -> COMMIT
                print("Success!!")
                self.connection.commit()
            else:
                #Error -> ROLLBACK
                print(f"Error : {exc_val}")
                self.connection.rollback()
                
                #Log the complete traceback
                if exc_tb:
                    logging.error(traceback.format_tb(exc_tb))
                    
                
        #Always close
        self.connection.close()
        logging.info("Connection closed")
        
            
        return False     
    