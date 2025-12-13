from pathlib import Path 
from re import sub,findall 
import requests 

class ImagesDownloader :
    def __init__(self):
        self._countries_images_paths = {
            'ksa':self.create_country_images_folder('ksa'),
            'uae':self.create_country_images_folder('uae')
        }

    def create_country_images_folder(self,country:str) -> Path:
        images_path = self.create_tree_of_folders(
            country,
            'assets',
            'img',
            'cars'
        )
        return images_path 

    def create_tree_of_folders(self,*paths:str) -> Path:
        path = Path(__file__).parents[1]
        for folder in paths :
            path = path.joinpath(folder)
            path.mkdir(exist_ok=True)
        return path
    
    def create_image_folder(self,variant_item:dict) -> Path:
        image_folder_path = self._countries_images_paths[
                self.get_location(variant_item['Make Model']['Link'])
            ].joinpath(
            self.clean_slug(variant_item['Make Model']['Slug'])
        )
        image_folder_path.mkdir(exist_ok=True)
        return image_folder_path
    
    def download(self,variant_item:dict):
        if not variant_item.get("Make Model"):
            return 
        index = 1
        while (variant_item["Make Model"].get(f"Logo {index}")):
            image_path = self.get_image_path(variant_item,index)
            if image_path.exists():
                print('Image is already downloaded')
                return 
            with open(image_path,'wb') as file:
                print(f'Downloading image {index} for : {variant_item["Make Model"]["Link"]}')
                try : 
                    response = requests.get(variant_item["Make Model"][f"Logo {index}"])
                except requests.exceptions.InvalidSchema:
                    continue
                except ConnectionError:
                    continue  
                except ConnectionResetError:
                    continue 
                file.write(response.content)
            index += 1

    def clean_slug(self,slug:str) -> str:
        cleaning_list = [
            '/'
        ]
        return sub('|'.join(cleaning_list),'-',slug)
    
    def get_image_path(self,variant_item:dict,image_id:int) -> Path:
        image_folder_path = self.create_image_folder(variant_item)
        return image_folder_path.joinpath(f'listing_main_{str(image_id).zfill(2)}.jpg')

    def get_location(self,url:str) -> str:
        return findall('//(\S+?)\.',url)[0]