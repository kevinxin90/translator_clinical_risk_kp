#!/usr/bin/env python
# coding: utf-8

# In[11]:


# Import Packages
import numpy as np
import pandas as pd
import sys
import json
import csv
import matplotlib.pyplot as plt

#filepath
new_node_filepath  = "/Users/basazinbelhu/Downloads/Translator/clinical_risk_kp/Datasets/clinical_risk_ehr_risk_nodes_data_2022_06_01.csv"
new_edge_filepath = "/Users/basazinbelhu/Downloads/Translator/clinical_risk_kp/Datasets/clinical_risk_ehr_risk_edges_data_2022_06_01.csv"
cut_off = 0


# In[12]:


def load_tsv_data(edge_filepath, node_filepath, cut_off):
    """
    This function takes two parameters: edge_filepath and the node_filepath.
    It will return a json formats that has the key of id, subject, predicate, object as the main keys. 
    """
    edges_data = pd.read_csv(edge_filepath, sep = ',')
    nodes_data = pd.read_csv(node_filepath, sep = ',')
    # generate the nodes atributes
    node_name_mapping = {}
    node_type_mapping = {}
    node_xref_mapping = {}
    for index, row in nodes_data.iterrows():
        node_name_mapping[row["id"]] = row["name"]
        node_type_mapping[row["id"]] = row["category"].split(':')[1] if str(row["category"]).startswith("biolink:") else row["category"]
        node_xref_mapping[row["id"]] = row["xref"]
        
    # generate the edges attributes
    
    for index, row in edges_data.iterrows():
        if row["p_value"] >= cut_off:
            if row["subject"] and row["predicate"] and row["subject"].split(':')[0] and row["object"].split(':')[0]:
                # Specify properties for subject
                subject = {
                    row["subject"].split(':')[0]: row["subject"],
                    "id": row["subject"],
                    "name": node_name_mapping[row["subject"]],
                    "type": node_type_mapping[row["subject"]]
                }
    #             current_xref = node_xref_mapping[row["subject"]]
                if ~np.isnan(node_xref_mapping[row["subject"]]):
                    subject[node_xref_mapping[row["subject"]].split(':')[0]] =  node_xref_mapping[row["subject"]]

                # Specify properties for object
                objects = {
                    row["object"].split(':')[0]: row["object"],
                    "id": row["object"],
                    "name": node_name_mapping[row["object"]],
                    "type": node_type_mapping[row["object"]]
                }
                if ~np.isnan(node_xref_mapping[row["object"]]):
                    objects[node_xref_mapping[row["object"]].split(':')[0]] =  node_xref_mapping[row["object"]]

                # Specify properties for predicate

                predicate = {
                    "type": row["predicate"].split(':')[-1] if row["predicate"].startswith("biolink:") else row["predicate"],
                    "original": row["predicate"],
                    "provided_by": row["provided_by"],
                    "provided_date": row["provided_date"],
                    "provenance": "https://github.com/NCATSTranslator/Translator-All/wiki/EHR-Risk-KP",
                    "category": row["category"].split(':')[1] if row["category"].startswith("biolink:") else row["category"],
                    "classifier": row["classifier"],
                    "relation": row["relation"],
                    "auc_roc": float(row["auc_roc"]),
                    "p_values": float(row["p_value"])
                }

                # conditional properties for predicate (if not Null)
                if ~np.isnan(row["feature_importance"]):
                    predicate["feature_importance"] =  float(row["feature_importance"])
                if ~np.isnan(row["feature_coefficient"]):
                    predicate["feature_coefficient"] = float(row["feature_coefficient"])
                    predicate["odd_ratio"] = np.exp(row["feature_coefficient"])

                # make a unique id from  subject, predicate, and object indentifiers
                if row["classifier"] == "Logistic Regression":
                    unique_id_list = [row["subject"], row["predicate"], row["object"], row["classifier"], str(row["auc_roc"]),
                                    str(row["feature_coefficient"])]
                else:
                    unique_id_list = [row["subject"], row["predicate"], row["object"], row["classifier"], str(row["auc_roc"]),
                                    str(row["feature_importance"])]
            json = {
                "id":'-'.join(unique_id_list),
                "subject": subject,
                "predicate": predicate,
                "object": objects
            }
            yield json
def main():
    count = 0
    verbose = True
    for row in load_tsv_data(new_edge_filepath, new_node_filepath, cut_off):
        if verbose:
            print(json.dumps(row, sort_keys= False, indent=2))
        count += 1
        if count >= 10:
           break
        
if __name__ == "__main__": 
    main() 

