class SystemParams:

    def update(self, settings):
        for k,v in settings.items():
            if k.startswith("system."):
                setattr(self, k[7:], v)

system_params = SystemParams()
