from disnake import commands


class PatchedContext(commands.Context):
    # TODO: Make this
    ...


class EditInvokeContext(PatchedContext):
    def _get_patch_message(self, content):
        msg = "This command was invoked by an edit"
        return msg if content is None else f"{msg}\n{content}"

    def send(self, content=None, **kwargs):
        return super().send(self._get_patch_message(content), **kwargs)

    def reply(self, content=None, **kwargs):
        return self.send(self._get_patch_message(content), **kwargs)
