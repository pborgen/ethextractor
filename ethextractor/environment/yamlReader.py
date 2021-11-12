import yaml

class YamlReader:

    def read(self, yaml_absolut_path):
        data = None

        with open(yaml_absolut_path) as f:
            # use safe_load instead load
            data = yaml.safe_load(f)

        return data
