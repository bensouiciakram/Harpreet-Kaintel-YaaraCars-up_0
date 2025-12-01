import shutil
from pathlib import Path

def create_output_file(template_name: str = 'template.xlsx', output_name: str = 'output.xlsx') -> Path:
    root = Path(__file__).parents[2]  
    template_path = root.joinpath(template_name)
    output_path = root.joinpath(output_name)
    if not output_path.exists():
        shutil.copy(template_path, output_path)
    return output_path