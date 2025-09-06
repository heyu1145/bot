class Helper()
    def get_all_commands(bot):
        """Return list of command objects"""
        return list(bot.tree.get_commands())

    def get_command_info(bot, cmd: str):
        """Return dict with command info or None if not found"""
        for command in bot.tree.get_commands():
            if command.name == cmd:
                return {
                    "name": command.name,
                    "description": command.description,
                    "options": command.options
                }
        return None

async def setup(bot):
    await bot.add_cog(Helper(bot))
