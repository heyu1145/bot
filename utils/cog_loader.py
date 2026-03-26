"""
Cog Auto-Loader Module
Provides automatic discovery and loading of cogs without manually editing bot.py
"""
import os
import logging
import importlib
from pathlib import Path
from typing import List, Optional
from discord.ext import commands

logger = logging.getLogger('discord')


class CogLoader:
    """
    Utility class for automatically loading cogs
    """
    def __init__(self, bot: commands.Bot, cogs_directory: str = "cogs"):
        """
        Initialize CogLoader
        
        Args:
            bot: Discord bot instance
            cogs_directory: Path to cogs directory
        """
        self.bot = bot
        self.cogs_directory = cogs_directory
        self.loaded_cogs = []
        self.failed_cogs = []

    def discover_cogs(self) -> List[str]:
        """
        Discover all cog modules in the cogs directory
        
        Returns:
            List containing all discovered cog module names
        """
        cogs = []
        cogs_path = Path(self.cogs_directory)
        
        if not cogs_path.exists():
            logger.error(f"❌ Cogs directory does not exist: {self.cogs_directory}")
            return cogs
            
        # Find all .py files (excluding __init__.py)
        for file_path in cogs_path.glob("*.py"):
            if file_path.name != "__init__.py":
                # Extract module name (without .py extension)
                module_name = f"{self.cogs_directory}.{file_path.stem}"
                cogs.append(module_name)
                
        return sorted(cogs)

    async def load_all_cogs(self, exclude_cogs: Optional[List[str]] = None) -> dict:
        """
        Automatically load all discovered cogs
        
        Args:
            exclude_cogs: List of cogs to exclude from loading
            
        Returns:
            Dictionary containing load results
        """
        if exclude_cogs is None:
            exclude_cogs = []
            
        discovered_cogs = self.discover_cogs()
        successful_loads = []
        failed_loads = []
        
        logger.info(f"🔍 Discovered {len(discovered_cogs)} cogs: {discovered_cogs}")
        
        for cog in discovered_cogs:
            # Check if in exclude list
            if cog in exclude_cogs:
                logger.info(f"⏭️  Excluding cog: {cog}")
                continue
                
            try:
                await self.bot.load_extension(cog)
                successful_loads.append(cog)
                self.loaded_cogs.append(cog)
                logger.info(f"✅ Successfully loaded cog: {cog}")
            except Exception as e:
                error_msg = f"❌ Failed to load cog {cog}: {str(e)}"
                logger.error(error_msg)
                failed_loads.append({
                    'cog': cog,
                    'error': str(e)
                })
                self.failed_cogs.append(cog)
        
        return {
            'successful': successful_loads,
            'failed': failed_loads,
            'total_discovered': len(discovered_cogs),
            'total_loaded': len(successful_loads),
            'total_failed': len(failed_loads)
        }

    async def reload_cog(self, cog_name: str) -> bool:
        """
        Reload a specific cog
        
        Args:
            cog_name: Name of the cog to reload
            
        Returns:
            Whether reload was successful
        """
        try:
            await self.bot.reload_extension(cog_name)
            logger.info(f"🔄 Successfully reloaded cog: {cog_name}")
            if cog_name not in self.loaded_cogs:
                self.loaded_cogs.append(cog_name)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reload cog {cog_name}: {str(e)}")
            return False

    async def unload_cog(self, cog_name: str) -> bool:
        """
        Unload a specific cog
        
        Args:
            cog_name: Name of the cog to unload
            
        Returns:
            Whether unload was successful
        """
        try:
            await self.bot.unload_extension(cog_name)
            logger.info(f"🗑️  Successfully unloaded cog: {cog_name}")
            if cog_name in self.loaded_cogs:
                self.loaded_cogs.remove(cog_name)
            if cog_name in self.failed_cogs:
                self.failed_cogs.remove(cog_name)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to unload cog {cog_name}: {str(e)}")
            return False

    def get_loaded_cogs(self) -> List[str]:
        """
        Get list of loaded cogs
        
        Returns:
            List of loaded cogs
        """
        return self.loaded_cogs.copy()

    def get_failed_cogs(self) -> List[str]:
        """
        Get list of failed cogs
        
        Returns:
            List of failed cogs
        """
        return self.failed_cogs.copy()

    def get_cogs_status(self) -> dict:
        """
        Get status information for all cogs
        
        Returns:
            Dictionary containing cogs status information
        """
        return {
            'loaded': self.get_loaded_cogs(),
            'failed': self.get_failed_cogs(),
            'total_loaded': len(self.loaded_cogs),
            'total_failed': len(self.failed_cogs)
        }


# Convenience function to quickly create and use CogLoader
async def setup_cogs(bot: commands.Bot, cogs_directory: str = "cogs", exclude_cogs: Optional[List[str]] = None) -> CogLoader:
    """
    Convenience function: Set up and load all cogs
    
    Args:
        bot: Discord bot instance
        cogs_directory: Path to cogs directory
        exclude_cogs: List of cogs to exclude
        
    Returns:
        CogLoader instance
    """
    loader = CogLoader(bot, cogs_directory)
    await loader.load_all_cogs(exclude_cogs)
    return loader