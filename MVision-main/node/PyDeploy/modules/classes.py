class PipelineStorage:
    def __init__(self):
        self.storage = {}

    def __str__(self):
        return str(self.storage)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.storage})"

    def __iter__(self):
        for pipeline_info in self.storage.values():
            yield pipeline_info['pipeline']

    def items(self):
        for name, info in self.storage.items():
            yield name, info

    def __getitem__(self, pipeline_name):
        return self.storage[pipeline_name]

    def add_pipeline(self, pipeline_name, sinks, pipeline_object, tee):
        if not isinstance(sinks, list):
            sinks = [sinks]
        self.storage[pipeline_name] = {
            "sinks": sinks,
            "pipeline": pipeline_object,
            "tee": tee
        }

    def get_pipeline(self, pipeline_name):
        return self.storage.get(pipeline_name)

    def update_pipeline(self, pipeline_name, sinks=None, pipeline_object=None, tee=None):
        if pipeline_name in self.storage:
            if sinks is not None:
                if not isinstance(sinks, list):
                    sinks = [sinks]
                self.storage[pipeline_name]["sinks"] = sinks
            if pipeline_object is not None:
                self.storage[pipeline_name]["pipeline"] = pipeline_object
            if tee is not None:
                self.storage[pipeline_name]["tee"] = tee

    def remove_pipeline(self, pipeline_name):
        if pipeline_name in self.storage:
            del self.storage[pipeline_name]
    
    def display_all_pipelines(self):
        all_pipelines_info = []
        for name, info in self.storage.items():
            sinks_info = ", ".join(info['sinks'])
            pipeline_info = f"Name: {name}, Sinks: {sinks_info}, Pipeline: {info['pipeline']}, Tee: {info.get('tee', 'N/A')}"
            all_pipelines_info.append(pipeline_info)
        return "\n".join(all_pipelines_info)
    
    def get_sinks(self, pipeline_name):
        pipeline_info = self.get_pipeline(pipeline_name)
        if pipeline_info:
            return pipeline_info["sinks"]
        return []