import tabula as tb
import pandas as pd
import PyPDF2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def parse(file):
    pdfReader = PyPDF2.PdfReader(file)
    totalPages = len(pdfReader.pages)

    i = 0
    while i<totalPages-1:
        if i==0:
            data_temp = tb.read_pdf(file, area = (320, 0, 660, 800), pages = 'all', pandas_options={'header': None, 'dtype': str}, stream=True)[i]
        else:
            data_temp = tb.read_pdf(file, area = (160, 0, 800, 800), pages = 'all', pandas_options={'header': None, 'dtype': str}, stream=True)[i]

        if (data_temp[data_temp.columns[-1]].eq('CR').any()):
            data_temp['amount'] = data_temp[data_temp.columns[-2]]
            data_temp['flag'] = np.where(data_temp[data_temp.columns[-2]].isnull(), 'DR', 'CR')
        else:
            data_temp['amount'] = data_temp[data_temp.columns[-1]]
            data_temp['flag'] = 'DR'

        data = data_temp[[0,2,'amount','flag']]
        data.columns = ['date', 'description', 'amount', 'flag']
        
        if i==0:
            df = data.copy()
        else:
            df = pd.concat([df,data], ignore_index=True)
        i+=1

    df['amount'] = df['amount'].str.replace(".", "")
    df['amount'] = pd.to_numeric(df['amount'])
    df.loc[df['flag'].str.contains('CR'), 'amount'] *= -1

    df_clean = df.loc[(df['date'].str.len() < 7) & (df['description'].str.len() > 4)]
    df_clean = df_clean[~df_clean['description'].isin(['PEMBAYARAN - MBCA'])]

    df_clean.to_csv("transaction.csv")

if __name__ == "__main__":
    text = input("Masukkan path ke PDF CC BCA anda:\n")
    parse(text)
    print("Done!")
