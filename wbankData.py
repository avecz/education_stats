import wbgapi as wb # API for the World Bank Database
from pandas import to_datetime

def fetch_and_clean_data(serie_id=None, serie_desc=None, db=12):
    """

    # database 'Education Statistics' (id 12)

    """

    # if no desc provided, fetch description with the World Bank API
    # will be the column name in the final dataframe
    if serie_desc == None:
        serie_desc = list(wb.series.list(serie_id, db=db))[0]['value']

    # fetch the selected series data
    df = wb.data.DataFrame(serie_id, db=db).reset_index()

    # tiding the dataframe
    # wide df to long df
    df = df.melt(id_vars=['economy'], value_name=serie_desc, var_name='year')
    # dropping the NaNs
    df.dropna(inplace=True)
    # remove extra characters in the column 'year' and format as datetime
    df['year'] = df['year'].str.replace('YR', '')
    df['year'] = to_datetime(df['year'], format='%Y')

    return df

def get_countries_data(df=None, id_column = 'id', description_column='name', agg_columns = ['region', 'adminregion', 'lendingType', 'incomeLevel']):
    """
    Function to get and format the list of countries with
    its classifications.
    
    """

    # auxiliaries variables
    aux_suffix_agg_columns_id = '_id'
    aux_suffix = '_y'

    if df == None:
        # fetch the data from World Bank API if no dataframe were passed.
        df = wb.economy.DataFrame().reset_index()
    
    df_temp = df.copy()
    
    # the agregate columns in reality have the id of each
    # aggregate, which we will merge with the id column
    # to get the the actual agregate data

    # append a suffix to current id columns
    agg_id_columns = [x+aux_suffix_agg_columns_id for x in agg_columns]
    rename_columns_dict = dict(zip(agg_columns,agg_id_columns))
    df_temp = df_temp.rename(columns=rename_columns_dict)
    
    for agg_id_col in agg_id_columns:
        agg_desc_col = agg_id_col.split(aux_suffix_agg_columns_id,maxsplit=1)[0]
        df_temp = df_temp.merge(df_temp[[id_column, description_column]],\
                        how='left',\
                        left_on=agg_id_col,\
                        right_on=id_column,suffixes=(None,aux_suffix))
        df_temp = df_temp.drop(id_column+aux_suffix,axis=1)
        df_temp = df_temp.rename(columns={description_column+aux_suffix:agg_desc_col})
    # filter out the aggregates rows
    df = df_temp[df_temp['aggregate']==False]
    
    # df is ready.
    # return the df with only the needed columns
    
    # first the id columns and the description columns using a list compreension.
    # (idea here https://www.geeksforgeeks.org/python-convert-list-of-tuples-into-list/)
    selected_columns = [item for tup in list(zip(agg_columns,agg_id_columns)) for item in tup]
    
    # add the 2 main collumns (id and country)
    selected_columns = [id_column, description_column] + selected_columns

    return df[selected_columns]