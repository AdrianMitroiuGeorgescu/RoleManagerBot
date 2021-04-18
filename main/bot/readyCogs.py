from glob import glob

COGS   = [path.split("\\")[-1][:-3] for path in glob(".cogs/*.py")]


class Ready(object):
    def __init__(self):
        self.allReady = all([getattr(self, cog) for cog in COGS])

        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog is ready")