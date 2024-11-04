import argparse
import mysql.connector
import pandas as pd
from mysql.connector import Error

class Database:
    """
        Initiate connection to MySQL database. Initialize self.cv_dict to get cultivar schema, use database argument to return schema name to self.cv
    """
    def __init__(self, host, user, port, database, password):
        self.cv_dict = {"arc": "oryza_sativa_arc_core_59_112_1", 
                "azucena": "oryza_sativa_azucena_core_59_112_1", 
                "chaomeo": "oryza_sativa_chaomeo_core_59_112_1", 
                "gobolsailbalam": "oryza_sativa_gobolsailbalam_core_59_112_1", 
                "ir64": "oryza_sativa_ir64_core_59_112_1", 
                "ketannangka": "oryza_sativa_ketannangka_core_59_112_1", 
                "khaoyaiguang": "oryza_sativa_khaoyaiguang_core_59_112_1", 
                "larhamugad": "oryza_sativa_larhamugad_core_59_112_1",  
                "lima": "oryza_sativa_lima_core_59_112_1", 
                "liuxu": "oryza_sativa_liuxu_core_59_112_1", 
                "mh63": "oryza_sativa_mh63_core_59_112_1", 
                "n22": "oryza_sativa_n22_core_59_112_1", 
                "natelboro": "oryza_sativa_natelboro_core_59_112_1", 
                "nipponbare" : "oryza_sativa_core_59_112_7",
                "nipponbare_otherfeatures": "oryza_sativa_otherfeatures_59_112_7",
                "pr106": "oryza_sativa_pr106_core_59_112_1", 
                "zs97": "oryza_sativa_zs97_core_59_112_1"}
        self.cv = self.cv_dict[database]
        
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                port=port,
                database=self.cv,
                password=password
                )
            print(f"Connected to {self.cv}!") 
        except Error as err:
            print(f"Error: '{err}'")
    
    """
        Execute SQL queries, stores results in list
    """
    def execute_query(self, query):
        cursor = self.connection.cursor() 
        try:
            cursor.execute(query)
            results = [list(row) for row in cursor.fetchall()]
            return results
        except Error as err:
            print(f"Error: '{err}'")
            
    """
        Query for gene IDs that do not have xref_ids for each cultivar. Filters out non "Os" genes for nipponbare (core schema), retains "LOC" genes for nipponbare otherfeatures
    """     
        
    def query_gene_ids_wo_xref(self):
        if self.cv == "oryza_sativa_core_59_112_7":
            nipponbare_id_wo_xref = f"""SELECT stable_id FROM {self.cv}.gene WHERE display_xref_id IS NULL AND stable_id LIKE 'Os%';"""
            return nipponbare_id_wo_xref
        elif self.cv == "oryza_sativa_otherfeatures_59_112_7":
            nipponbare_of_id_wo_xref = f"""SELECT stable_id FROM {self.cv}.gene WHERE stable_id LIKE 'LOC%';"""
            return nipponbare_of_id_wo_xref
        else:
            gene_id_wo_xref = f"""SELECT stable_id FROM {self.cv}.gene WHERE display_xref_id IS NULL;"""
            return gene_id_wo_xref

    """ 
        Query for gene IDs that have existing xref_ids for each cultivar. Filters out non "Os" genes for nipponbare (core schema). Nipponbare otherfeatures does not have any genes with existing xref_ids, hence pass
    """

    def query_genes_with_existing_xref(self):
        if self.cv == "oryza_sativa_core_59_112_7":
            nipponbare_genes_w_xref = f"""SELECT display_xref_id, stable_id FROM {self.cv}.gene WHERE display_xref_id IS NOT NULL AND stable_id LIKE 'Os%';"""
            return nipponbare_genes_w_xref
        elif self.cv == "oryza_sativa_otherfeatures_59_112_7":
            pass
        else:
            genes_w_xref = f"""SELECT display_xref_id, stable_id FROM {self.cv}.gene WHERE display_xref_id IS NOT NULL;"""
            return genes_w_xref
    
    """
        Query for fetching maximum existing xref_id in each schema (to avoid overwriting existing xref_ids). No existing xref_ids in nipponbare. 
    """    
    def query_max_existing_xref_id(self):
        if self.cv != "oryza_sativa_otherfeatures_59_112_7":
            max_xref_id = f"""SELECT MAX(xref_id) FROM {self.cv}.xref;"""
            return max_xref_id

    """
        Query for populating schema.xref table with xref_id, stable_id etc
    """
    
    def populate_xref(self, stable_id, xref_id):
        action = f"""INSERT INTO {self.cv}.xref 
                        (`xref_id`, `external_db_id`, `dbprimary_acc`, `display_label`, `version`, `info_type`, `info_text`) 
                        VALUES ({xref_id}, '50916', '{stable_id}', '{stable_id}', '0', 'DEPENDENT', '');"""
        return action
    
    """
        Query for updating schema.gene with the newly assigned xref_ids corresponding to stable_id
    """
    
    def update_gene(self, stable_id, xref_id):
        action = f"""UPDATE {self.cv}.gene 
                        SET display_xref_id = {xref_id}
                        WHERE stable_id = '{stable_id}';"""
        return action 
    
    """
        Query for populating schema.external_synonym with pangene_ids and their corresponding xref_ids (taken from joined pandas df from joined_df())
    """
    
    def populate_external_synonym(self, xref_id, pangene_id):
        action = f"""INSERT INTO {self.cv}.external_synonym 
                        (`xref_id`, `synonym`)
                        VALUES ({xref_id}, '{pangene_id}');"""
        return action 

    """
        Iterate through data frame using itertuples() containing stable_ids and xref_ids for each cultivar, and execute populate_xref() and update_gene() as queries in execute_query()
    """

    def upload_xref_and_genes(self, table):
        self.table = table
        for row in table.itertuples(index=True):
            xref_id = getattr(row, 'xref_id')
            stable_id = getattr(row, 'stable_id')
            
            print(self.populate_xref(stable_id, xref_id)) # print commands to screen to check, keep self.execute_query() commands hashed out until confident queries are correct
            print(self.update_gene(stable_id, xref_id))
            self.execute_query(self.populate_xref(stable_id, xref_id))               
            self.execute_query(self.update_gene(stable_id, xref_id))
               
        print("Xref and gene upload finished!")
            
    """
        Iterate through data frame using itertuples() containing pangene_ids and xref_ids (created using .join_df(), and execute populate_external_synonym() as query in execute_query()
    """
    def upload_external_synonym(self, table):
        self.table = table
        for row in table.itertuples(index=True):
            xref_id = getattr(row, 'xref_id')
            pangene_id = getattr(row, 'pangene_id')
            print(self.populate_external_synonym(xref_id, pangene_id))
            self.execute_query(self.populate_external_synonym(xref_id, pangene_id))
        
        print("External synonym upload finished!")
    
    """
        Retrieve gene stable ids as a list by executing get_gene_ids_wo_xref() query in execute_query()
    """
    
    def get_gene_ids(self):
        gene_ids = self.execute_query(self.query_gene_ids_wo_xref())
        gene_ids = [field[0] for field in gene_ids]
        
        return gene_ids
    
    """
        Retrieve maximum existing xref_id for schema by executing get_max_existing_xref_id() query in execute_query(), then assign new xref_ids starting from max existing xref_id + 1
        If database is nipponbare otherfeatures, assign xref_ids starting from 1
        Store stable_ids (retrieved via get_gene_ids()) and xref_ids in dict and return as pandas df
    """
    
    def get_xref_ids(self):
        if self.cv != "oryza_sativa_otherfeatures_59_112_7":
            max_xref = self.execute_query(self.query_max_existing_xref_id())[0][0]
            xref_ids = range(max_xref+1, max_xref+len(self.get_gene_ids())+1)
            
            dict = {"stable_id": self.get_gene_ids(),
                    "xref_id": xref_ids}
            xref_table = pd.DataFrame(dict)
            
            return xref_table
        else:
            xref_ids = range(1, len(self.get_gene_ids())+1)
            dict = {"stable_id": self.get_gene_ids(),
                    "xref_id": xref_ids}
            xref_table = pd.DataFrame(dict)
            return xref_table

    """
        Retrieve gene_id and xref_id as lists for genes that have existing xref_ids in each schema. 
        Store existing gene_ids and existing xref_ids in dict, and return as pandas df
    """

    def get_existing_ids(self):
        existing = self.execute_query(self.query_genes_with_existing_xref())
        existing_xref_ids = [field[0] for field in existing]
        existing_gene_ids = [field[1] for field in existing]
            
        dict = {"stable_id": existing_gene_ids,
                "xref_id": existing_xref_ids}
        existing_df = pd.DataFrame(dict)

        return existing_df
    
    """
        Add command line arguments for host, port, database and password
    """
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Upload CV names")
        parser.add_argument("--host", help="Host", action="store", dest="host", required=True)
        parser.add_argument("-u", "--user", help="User", action="store", dest="user", required=True)
        parser.add_argument("-p", "--port", help="Port", action="store", dest="port", required=True)
        parser.add_argument("-d", "--database", help="Database", action="store", dest="database", required=True) 
        parser.add_argument("-pw", "--password", help="Password", action="store", dest="password")
        args = parser.parse_args()
        return args

class PangeneMatrixProcessor():
    
    def __init__(self, matrix):
         self.matrix = matrix
        
    """
        Read parsed pangene matrix 
    """    
    def parse_pangene_matrix(self):
        with open (self.matrix, 'r') as matrix_file:
            matrix_df = pd.read_csv(matrix_file, sep='\t')

        return matrix_df

    """
        Join pangene matrix with xref_id table (from get_xref_ids()) or existing_id table (from get_missing_ids()) using INNER JOIN on stable_id.
        Drop Unnamed: 0 column.
    """

    def join_df(self, table, matrix):
        joined_df = pd.merge(table, matrix, on='stable_id', how ="inner")
        joined_df = joined_df.drop('Unnamed: 0', axis = 1)
        
        return joined_df

def main():
    """
        if running on nipponbare_otherfeatures, hash out existing_table and db.upload_external_synonym()
    """
    args = Database.parse_args()
    db = Database(args.host, args.user, args.port, args.database, args.password) # initialize Database object with user arguments from parse_args()
    tb = PangeneMatrixProcessor("pangene_matrix_genes_transformed.tab") # initialize Matrix 
    matrix = tb.parse_pangene_matrix() # read pangene matrix

    xref_table = db.get_xref_ids() # generate xref_table containing gene_ids and xref_ids 
    joined_table = tb.join_df(matrix, xref_table) # join pangene matrix with xref_table

    existing_table = db.get_existing_ids() # generate existing table containing gene_ids and xref_ids for genes with existing xref_ids 
            
    existing_table_w_pangeneids = tb.join_df(existing_table, matrix) # join pangene matrix with existing table generated in command above
    
    db.upload_xref_and_genes(xref_table)  # execute query to upload xref_ids and stable_ids to schema.xref, and update schema.gene
    db.upload_external_synonym(joined_table) # execute query to upload xref_ids and pangene_ids into schema.external_synonym
    db.upload_external_synonym(existing_table_w_pangeneids) # execute query to upload xref_ids and pangene_ids for stable_ids that already had an xref_id assigned to them into schema.external_synonym
    
   
if __name__ == "__main__":
    main()
