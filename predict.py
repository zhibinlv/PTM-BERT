import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from biotransformers import BioTransformers
import torch
import Bio
import joblib
from sklearn.linear_model import LogisticRegression
import sklearn as sk
import argparse
from biotransformers import BioTransformers
print(sk.__version__)
print(torch.__version__)
print(Bio.__version__)

from Bio import SeqIO

def read_fasta(fastain):
    records = list(SeqIO.parse(fastain,"fasta"))
    id_seqs=[]
    for i in range(len(records)):
        id=str(records[i].id)
        ss=str(records[i].seq)
        id_seqs.append([id,ss])
    
    id_seqs=pd.DataFrame(id_seqs,columns=["ID","Seq"])
    
    print("Read fasta file DONE!")
    return id_seqs

def Emb_BERT_bfd(data_pd):
    FeatureName=["protbert_bfd"+str(i+1) for i in range(1024)]
    sequences=data_pd["Seq"]
     
    
    
    bio_trans = BioTransformers(backend="protbert_bfd",num_gpus=1)
    embeddings = bio_trans.compute_embeddings(sequences, pool_mode=('cls','mean'),batch_size=2)

     
    mean_emb = embeddings['mean']
     
    ABaf=pd.DataFrame(mean_emb)
    ABaf.columns=FeatureName
    ABaf=pd.concat([data_pd,ABaf],axis=1)
    print(ABaf.shape)
    print("SEQUENCES embbeding DONE!")
    
    
    return ABaf
    
    
    





def predict(data_pd,out,std="./ML_Models/MainStandardScaler.joblib",model="./ML_Models/Best.model.joblib"):
    bestFeat=pd.read_csv("./ML_Models/FeatName1024.csv",header=0)
    col_name=bestFeat.columns
    
    data=data_pd
     
    std=joblib.load(std)
    model=joblib.load(model)
     
    
    X=data[col_name]
    X=std.transform(X)
     
    Xt=X[:,:810]
    
    y_pred=model.predict(Xt)
    y_pred_prob=model.predict_proba(Xt)
     
    
    print(y_pred_prob.shape)
    
    print(y_pred)
    
    print("Prediction DONE!")
    
    
    
    yout=pd.DataFrame(y_pred,columns=["Label"])
    yout["Protein_Type"]=""
    for i in range(len(y_pred)):
        if y_pred[i]==0:
            yout["Protein_Type"][i]="Mesophilic"
       
        if y_pred[i]==1:
            yout["Protein_Type"][i]="Thermophilic"
        if y_pred[i]==2:
            yout["Protein_Type"][i]="Psychrophilic"
         
    #return output
    yout["Seq"]=data_pd["Seq"]
    yout.to_csv(out,index=False)



if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Input a Fasta file, output the predction results in CSV')
 
    
    parser.add_argument('--infasta', type=str, default="./Data/test.fasta")
    parser.add_argument('--out', type=str, default="Results.Pred.csv")
 
    
    args = parser.parse_args()
    print(args)
    inFasta = args.infasta
    out = args.out+".res.pred.csv"
    fasta_pd=read_fasta(inFasta)
    data_pd=Emb_BERT_bfd(fasta_pd)
    
    predict(data_pd,out)
    
     
    print("Plese see the predction results in ", out)
 
