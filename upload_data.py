import csv
import json 
from pathlib import Path 
from typing import Callable 
from re import sub,findall
import pandas as pd 
import numpy as np 
from pandas import DataFrame
from pandas.core.series import Series 
from playwright.sync_api import sync_playwright,Page


class Uploader:

    table_url_template = 'https://staging.yaaracars.com/login/cars/{table_name}.php'
    currencies = {
        'KSA':'AED',
        'UAE':'SAR'
    }

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page() 
        self.login(
            'vaishali@arabyads.com',
            'Vaishali@Yaara123',
        )
        self.dfs = pd.read_excel('output.xlsx',sheet_name=None)
        self.load_config()
        # self.update_brands()
        # self.update_models()
        # self.update_variants()
        self.update_measurement()
        self.update_features()
        self.update_safety()
        self.update_exterior()
        self.update_interior()

    def create_dataframe(self,table_name:str) -> DataFrame:
        table_config = self.config[table_name]
        df = pd.DataFrame(
            {
                item['name']:pd.Series(dtype=item['type'])
                for item in table_config['columns']
            }
        )
        for item in table_config['columns']:
            if item['maping']:
                df[item['name']] = self.dfs[item['maping'][0]][item['maping'][1]]
        return df 

    def login(self,email:str,passwd:str):
        # self.page.goto('https://staging.yaaracars.com/admin')
        self.page.goto('https://staging.yaaracars.com/login.php')
        self.page.fill('//input[@name="username"]',email)
        self.page.fill('//input[@name="password"]',passwd)
        self.page.click('//button[@name="login"]')

    def export_table_file(self,table_name:str) -> str:
        self.page.goto(
            self.table_url_template.format(
                table_name=table_name
            )
        )
        with self.page.expect_download() as download_value:
            self.page.click('//input[@name="export_btn"]')
        download = download_value.value 
        filename = download.suggested_filename
        download.save_as(filename)
        self.clean_empty_row(filename)
        return filename
    
    def clean_empty_row(self,filename:str):
        with open(filename,'r') as file:
            cleaned_file_content = file.read().strip()
        with open(filename,'w') as file:
            file.write(cleaned_file_content)

    def add_row(self,filename:str,row:list[str]):
        with open(filename,'a',newline='',encoding='utf-8') as file :
            writer = csv.writer(file)
            writer.writerow(['']+row)

    def update_brands(self):
        brands_df = self.create_dataframe('brands')
        brands_df['Location'] = self.dfs['Description']['Url']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        brands_df['Currency'] = brands_df['Location'].apply(lambda v:self.currencies[v])
        brands_df['Brand_Slug'] = brands_df['Brand'].apply(self.create_slug)

        brands_df.loc[len(brands_df)] = {
            "Master_ID":1000,
            "Location": "JP",
            "Currency":"SAR",
            "Year": 2024,
            "Brand": "Toyota",
            "Brand_Slug": "Corolla",
            "Brand_logo":"",
            "Content":""
        }
        brands_df.loc[len(brands_df)] = {
            "Master_ID":1001,
            "Location": "DZ",
            "Currency":"SAR",
            "Year": 2024,
            "Brand": "Toyota",
            "Brand_Slug": "Corolla",
            "Brand_logo":"",
            "Content":""
        }
        filename = self.export_table_file('brand')
        original_brands_df = pd.read_csv(filename)
        all_brands = pd.concat(
            [
                original_brands_df,
                self.filter_table(
                    self.check_existing_brand,
                    brands_df,
                    original_brands_df,
                    'Location',
                    'Brand',
                    'Year'
                )
            ]
        )
        all_brands['Brand_logo'] = all_brands['Brand'].apply(
            lambda v:self.get_existing_logo(all_brands,v)
        )
        brands_filename = 'all_brands.csv'
        all_brands.to_csv(brands_filename)
        # self.upload_file('brand',brands_filename)
        breakpoint()

    def update_models(self):
        modals_df = self.create_dataframe('modals')
        modals_df['Location_meta'] = self.dfs['Description']['Url']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        modals_df['Modal_Slug'] = modals_df['Modal'].apply(lambda v:self.create_slug(v)) 
        modals_df['Modal'] = modals_df[['Modal','Brand_meta']].apply(
            lambda row:sub(f'\d{{4}}|New|{row["Brand_meta"]}','',row['Modal']),axis=1
        )
        modals_df['Modal'] = modals_df['Modal'].apply(lambda v:v.strip())
        modals_df['Status_Modal'] = 'Draft'
        brands_df = self.get_table_dataframe('brand')
        modals_df['Brand_ID'] = modals_df.apply(
            lambda row:self.get_id(
                'Master_ID',
                brands_df,
                Location=row['Location_meta'],
                Year=row['Year_meta'],
                Brand=row['Brand_meta'],
                )
                ,axis=1
            )

        original_modals_df = self.get_table_dataframe('modal')

        modals_df.loc[len(modals_df)] = {
            "Mod_ID":1001,
            "Modal": "avenza2",
            "Modal_Slug":"avenza",
            "Brand_ID": 123,
            "Body_Type": "SUV",
            "Status_Modal":"Draft",
            "Location_meta":"KSA",
            "Year_meta":2023,
            "Brand_meta":"Toyota",
        }
        modals_df.loc[len(modals_df)] = {
            "Mod_ID":1001,
            "Modal": "avenza3",
            "Modal_Slug":"avenza",
            "Brand_ID": 123,
            "Body_Type": "SUV",
            "Status_Modal":"Draft",
            "Location_meta":"KSA",
            "Year_meta":2024,
            "Brand_meta":"Toyota",
        }

        idx = []
        for index,row in modals_df.iterrows():
            if not bool((original_modals_df['Modal'] == row['Modal']).any()):
                idx.append(index)
        
        filtered_modals_df = modals_df.loc[idx]
        all_models = pd.concat([original_modals_df,filtered_modals_df])
        all_models = all_models.drop(columns=[col for col in all_models.columns if 'meta' in col])
        modals_filename = 'all_modals.csv'
        all_models.to_csv(modals_filename)
        # self.upload_file('modal',modals_filename)

    def update_variants(self):
        variants_df = self.create_dataframe('variants')
        variants_df = variants_df.dropna(subset=['Brand_meta'])
        variants_df['Status'] = 'Draft'
        variants_df['Created_At'] = '0000-00-00 00:00:00'
        variants_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        variants_df['Var_Location'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        brands_df = self.get_table_dataframe('brand')
        variants_df['Ref_Brand'] = variants_df.apply(
            lambda row:self.get_id(
                'Master_ID',
                brands_df,
                Location=row['Location_meta'],
                Year=row['Year_meta'],
                Brand=row['Brand_meta'],
                )
                ,axis=1
            )
        modals_df = self.get_table_dataframe('modal')
        variants_df['Modal_ID'] = variants_df['Ref_Modal'].apply(lambda v:self.get_model_id(modals_df,v))
        # droping duplicate (repetitive variants) --------------------------------#
        original_variants_df = self.get_table_dataframe('variants')

        variants_df.loc[len(variants_df)] = {
            "Location_meta": "KSA",
            "Year_meta": 2024,
            "Brand_meta": "Toyota",
            "Var_ID": 10001,
            "Variant": "GX 2.5L-----------",
            "Ref_Modal": 5001,
            "Variant_Slug": "gx-25l",
            "Var_Location": "KSA",
            "Price": 135000.0,
            "Modal_ID": 3001,
            "Ref_Brand": 101,
            "Engine": "2.5L",
            "Cylinders": 4,
            "Drive_Type": "FWD",
            "Fuel_Tank": 60.0,
            "Fuel_Economy": 7.8,
            "Fuel_Type": "Petrol",
            "Horsepower": 203.0,
            "Torque": 250.0,
            "Transmission": "Automatic",
            "Seating_Capacity": 5,
            "Acceleration": 8.9,
            "Battery_Size": pd.NA,
            "Battery_Range": pd.NA,
            "Motor": pd.NA,
            "Top_Speed": 210.0,
            "Featured_Image": pd.NA,
            "Gallery": "img1.jpg,img2.jpg",
            "Status": "Draft",
            "Created_At": "2024-01-01"
        }

        variants_df.loc[len(variants_df)] = {
            "Location_meta": "UAE",
            "Year_meta": 2023,
            "Brand_meta": "Toyota",
            "Var_ID": 10002,
            "Variant": "Hybrid LE-------------",
            "Ref_Modal": 5001,
            "Variant_Slug": "hybrid-le",
            "Var_Location": "UAE",
            "Price": 148500.0,
            "Modal_ID": 3001,
            "Ref_Brand": 101,
            "Engine": "2.5L Hybrid",
            "Cylinders": 4,
            "Drive_Type": "AWD",
            "Fuel_Tank": 55.0,
            "Fuel_Economy": 4.2,
            "Fuel_Type": "Hybrid",
            "Horsepower": 215.0,
            "Torque": 270.0,
            "Transmission": "CVT",
            "Seating_Capacity": 5,
            "Acceleration": 7.6,
            "Battery_Size": 1.6,
            "Battery_Range": 50.0,
            "Motor": "Electric Assist",
            "Top_Speed": 200.0,
            "Featured_Image": pd.NA,
            "Gallery": "img3.jpg,img4.jpg",
            "Status": "Draft",
            "Created_At": "2023-06-15"
        }
        ids = []
        for index,row in variants_df.iterrows():
            if not (
                (original_variants_df['Variant'] == row['Variant']) &
                (original_variants_df['Var_Location'] == row['Var_Location']) 
            ).any():
                ids.append(index)

        filtered_df = variants_df.loc[ids]
        all_variants_df = pd.concat(
            [
                original_variants_df,
                filtered_df
            ], ignore_index=True
        )
        # all_variants_df=all_variants_df[~all_variants_df['Modal_ID'].isna()]
        all_variants_df = all_variants_df.drop(columns=[col for col in all_variants_df.columns if 'meta' in col])
        variants_filename = 'all_variants.csv'
        all_variants_df.to_csv(variants_filename)
        # self.upload_file('variants',variants_filename)











    def update_measurement(self):
        measurement_df = self.create_dataframe('measurement')
        measurement_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        measurement_df = measurement_df.dropna(subset=['Location_meta'])
        # getting variant_id --------------------------------------------#
        variants_df = self.get_table_dataframe('variants')
        measurement_df['Var_ID'] = measurement_df[["Variant_meta","Location_meta"]].apply(
            lambda row:self.get_variant_id(variants_df,row['Variant_meta'],row['Location_meta']),
            axis=1
        )
        original_measurement_df = self.get_table_dataframe('measurement')
        all_measurements_df = pd.concat([original_measurement_df,measurement_df])
        all_measurements_df=all_measurements_df[~all_measurements_df['Variant_ID'].isna()]
        all_measurements_df = all_measurements_df.drop(columns=[col for col in all_measurements_df.columns if 'meta' in col])
        measurement_filename = 'all_measurements.csv'
        all_measurements_df.to_csv(measurement_filename)
        # self.upload_file('measurement',measurement_filename)








    def update_features(self):
        features_df = self.create_dataframe('features')
        features_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        features_df = features_df.dropna(subset=['Location_meta'])
        # getting variant_id --------------------------------------------#
        variants_df = self.get_table_dataframe('variants')
        features_df['Var_ID'] = features_df[["Variant_meta","Location_meta"]].apply(
            lambda row:self.get_variant_id(variants_df,row['Variant_meta'],row['Location_meta']),
            axis=1
        )
        original_features_df = self.get_table_dataframe('features')
        all_features_df = pd.concat([original_features_df,features_df])
        all_features_df=all_features_df[~all_features_df['Variant_ID'].isna()]
        all_features_df = all_features_df.drop(columns=[col for col in all_features_df.columns if 'meta' in col])
        features_filename = 'all_features.csv'
        all_features_df.to_csv(features_filename)
        # self.upload_file('features',all_features_df)


    def update_safety(self):
        safety_df = self.create_dataframe('safety')
        safety_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        safety_df = safety_df.dropna(subset=['Location_meta'])
        # getting variant_id --------------------------------------------#
        variants_df = self.get_table_dataframe('variants')
        safety_df['Var_ID'] = safety_df[["Variant_meta","Location_meta"]].apply(
            lambda row:self.get_variant_id(variants_df,row['Variant_meta'],row['Location_meta']),
            axis=1
        )
        original_safety_df = self.get_table_dataframe('safety')
        all_safety_df = pd.concat([original_safety_df,safety_df])
        all_safety_df=all_safety_df[~all_safety_df['Variant_ID'].isna()]
        all_safety_df = all_safety_df.drop(columns=[col for col in all_safety_df.columns if 'meta' in col])
        safety_filename = 'all_safety.csv'
        all_safety_df.to_csv(safety_filename)
        # self.upload_file('safety',all_safety_df)

    def update_exterior(self):
        exterior_df = self.create_dataframe('exterior')
        exterior_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        exterior_df = exterior_df.dropna(subset=['Location_meta'])
        # getting variant_id --------------------------------------------#
        variants_df = self.get_table_dataframe('variants')
        exterior_df['Var_ID'] = exterior_df[["Variant_meta","Location_meta"]].apply(
            lambda row:self.get_variant_id(variants_df,row['Variant_meta'],row['Location_meta']),
            axis=1
        )
        original_exterior_df = self.get_table_dataframe('exterior')
        all_exterior_df = pd.concat([original_exterior_df,exterior_df])
        all_exterior_df=all_exterior_df[~all_exterior_df['Variant_ID'].isna()]
        all_exterior_df = all_exterior_df.drop(columns=[col for col in all_exterior_df.columns if 'meta' in col])
        exterior_filename = 'all_exterior.csv'
        all_exterior_df.to_csv(exterior_filename)
        # self.upload_file('exterior',all_exterior_df)


    def update_interior(self):
        interior_df = self.create_dataframe('interior')
        interior_df['Location_meta'] = self.dfs['Make Model']['Link']\
                                    .str.extract('//(\S+?)\.')[0]\
                                    .str.upper()
        interior_df = interior_df.dropna(subset=['Location_meta'])
        # getting variant_id --------------------------------------------#
        variants_df = self.get_table_dataframe('variants')
        interior_df['Var_ID'] = interior_df[["Variant_meta","Location_meta"]].apply(
            lambda row:self.get_variant_id(variants_df,row['Variant_meta'],row['Location_meta']),
            axis=1
        )
        original_interior_df = self.get_table_dataframe('interior')
        all_interior_df = pd.concat([original_interior_df,interior_df])
        all_interior_df=all_interior_df[~all_interior_df['Variant_ID'].isna()]
        all_interior_df = all_interior_df.drop(columns=[col for col in all_interior_df.columns if 'meta' in col])
        interior_filename = 'all_interior.csv'
        all_interior_df.to_csv(interior_filename)
        # self.upload_file('interior',all_interior_df)

    

    def get_existing_brands(self,page:Page) -> list[str]:
        return [
            handle.inner_text().lower()
            for handle in page.query_selector_all('//select[@name="brand"]/option')
        ]

    def get_years(self,page:Page) -> list[str]:
        return [
            handle.inner_text() 
            for handle in page.query_selector_all('//select[@name="year"]/option')
        ]
    
    def get_location(self,url:str) -> str:
        if type(url) is not str:
            return ''
        return findall('//(\S+?)\.',url)[0].upper() \
            if  findall('//(\S+?)\.',url) else ''
    
    def create_slug(self,title:str) -> str:
        cleaning_list = [
            '\s+',
            '/',
            '\(',
            '\)'
        ]
        title = sub('|'.join(cleaning_list),'-',title.lower())
        title = sub('-+','-',title)
        return title.strip('-')

    def get_existing_logo(self,brands_df:DataFrame,brand:str) -> str|None:
        logos = [logo for logo in brands_df[brands_df['Brand'] == brand]['Brand_logo'].values.tolist()]
        logos = [logo for logo in logos if logo]
        if not logos :
            return None
        return logos[0]
    
    def clean_model(self,raw_model:str,brand:str) -> str:
        second_part = raw_model.split(brand)[-1]
        return sub('\d{4}','',second_part).strip()

    def get_modal_id(self,models_df:DataFrame,model:str) -> int:
        return models_df[models_df['Modal'] == model]['Mod_ID'].values.tolist()[0]

    def get_variant_id(self,variants_df:DataFrame,variant:str) -> int:
        return variants_df[variants_df['Variant']==variant]['Var_ID'].values.tolist()[0]
    
    def load_config(self):
        self.config = json.load(open('config/upload_config.json'))

    def upload_file(self,table_name:str,filename:str):
        self.page.goto(f'https://staging.yaaracars.com/login/cars/{table_name}.php')
        self.page.set_input_files(
            '//input[@type="file"]',
            Path(__file__).parent.joinpath(filename)
        )
        self.page.click('//input[@name="import_btn"]')

    def check_existing_brand(self,df:DataFrame,**kwargs) -> bool:
        mask = pd.Series(True, index=df.index)
        for col, val in kwargs.items():
            mask &= df[col] == val
        return mask.any()
    
    def check_existing_modal(self,df:DataFrame,**kwargs) -> bool:
        mask = pd.Series(True, index=df.index)
        for col, val in kwargs.items():
            mask &= df[col] == val
        pass 

    def filter_table(self,check_func:Callable,df:DataFrame,original_df:DataFrame,*args) -> DataFrame:
        idx = []
        for index,row in df.iterrows():
            if not check_func(
                original_df,
                **{key:row[key] for key in args}
            ):
                idx.append(index)
        return df.loc[idx]

    def get_table_dataframe(self,table_name:str) -> DataFrame:
        filename = self.export_table_file(table_name)
        return pd.read_csv(filename)    
    
    
    def get_id(self,id_column:str,df:DataFrame,**kwargs) -> int :
        mask = pd.Series(True, index=df.index)
        for col, val in kwargs.items():
            mask &= df[col] == val
        ids = df[mask][id_column].values.tolist()
        if len(ids) == 0:
            breakpoint()
        return ids[0]
    
    def get_model_id(self,models_df:DataFrame,model:str) -> int:
        ids = models_df[models_df['Modal']==model]['Mod_ID'].values.tolist()
        try: 
            return ids[0]
        except IndexError:
            return np.nan
        
    def get_variant_id(self,variants_df:DataFrame,variant:str,location:str) -> int:
        ids = variants_df[(variants_df['Variant']==variant) & (variants_df['Var_Location']==location)]['Var_ID'].values.tolist()
        try :
            return ids[0]
        except IndexError:
            np.nan

if __name__ == '__main__':
    uploader = Uploader()