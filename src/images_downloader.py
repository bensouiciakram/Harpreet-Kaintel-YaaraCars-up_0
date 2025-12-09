from pathlib import Path 
from re import sub 
import requests 

class ImagesDownloader :
    def __init__(self):
        self._images_root_path = self.create_images_folder() 

    def create_images_folder(self) -> Path:
        images_path = self.create_tree_of_folders(
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
        image_folder_path = self._images_root_path.joinpath(
            self.clean_slug(variant_item['Make Model']['Slug'])
        )
        image_folder_path.mkdir(exist_ok=True)
        return image_folder_path
    
    def download(self,variant_item:dict):
        image_path = self.get_image_path(variant_item)
        if image_path.exists():
            print('Image is already downloaded')
            return 
        with open(image_path,'wb') as file:
            print(f'Downloading image for : {variant_item["Make Model"]["Link"]}')
            response = requests.get(variant_item["Make Model"]["Logo 1"])
            file.write(response.content)

    def clean_slug(self,slug:str) -> str:
        cleaning_list = [
            '/'
        ]
        return sub('|'.join(cleaning_list),'-',slug)
    
    def get_image_path(self,variant_item:dict) -> Path:
        image_folder_path = self.create_image_folder(variant_item)
        return image_folder_path.joinpath('1.jpeg'
            # self._variant_item['']
        )

