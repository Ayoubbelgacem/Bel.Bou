import os
import toml

class Config:
    def __init__(self, path="boubel.toml"):
        self.path = path
        self.data = {}
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.data = toml.load(f)

    def get_package_name(self):
        return self.data.get('package', {}).get('name', None)

    def get_version(self):
        return self.data.get('package', {}).get('version', '0.1.0')

    def get_dependencies(self):
        return self.data.get('dependencies', {})

    def get_dev_dependencies(self):
        return self.data.get('dev-dependencies', {})

    def save(self, path=None):
        if path is None:
            path = self.path
        with open(path, 'w', encoding='utf-8') as f:
            toml.dump(self.data, f)

    @staticmethod
    def create_default(path="boubel.toml"):
        if os.path.exists(path):
            return
        default = {
            'package': {
                'name': 'mon_projet',
                'version': '0.1.0',
                'description': 'Un projet Bou.Bel'
            },
            'dependencies': {},
            'dev-dependencies': {}
        }
        with open(path, 'w', encoding='utf-8') as f:
            toml.dump(default, f)
        return Config(path)