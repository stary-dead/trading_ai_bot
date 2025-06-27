"""
Configuration loader with environment variable support.
"""
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Load configuration from JSON with environment variable support."""
    
    def __init__(self, config_path: str = "config.json", env_path: str = ".env"):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the JSON configuration file
            env_path: Path to the .env file
        """
        self.config_path = config_path
        self.env_path = env_path
        self._config = None
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file and environment variables.
        
        Returns:
            Dictionary containing the complete configuration
        """
        if self._config is not None:
            return self._config
            
        # Load environment variables
        load_dotenv(self.env_path)
        
        # Load base configuration from JSON
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Inject environment variables
        self._inject_env_vars(config)
        
        self._config = config
        return config
    
    def _inject_env_vars(self, config: Dict[str, Any]) -> None:
        """
        Inject environment variables into the configuration.
        
        Args:
            config: Configuration dictionary to modify
        """
        # Exchange configuration
        if 'exchange' in config:
            config['exchange']['api_key'] = os.getenv('BINANCE_API_KEY', '')
            config['exchange']['api_secret'] = os.getenv('BINANCE_API_SECRET', '')
            
            # Update testnet setting based on environment
            environment = os.getenv('ENVIRONMENT', 'testnet').lower()
            config['exchange']['testnet'] = environment == 'testnet'
            
            if environment == 'production':
                config['exchange']['base_url'] = 'https://fapi.binance.com'
        
        # AI configuration
        if 'ai' in config:
            config['ai']['claude_api_key'] = os.getenv('CLAUDE_API_KEY', '')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'exchange.api_key')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        config = self.load()
        
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def validate_required_keys(self) -> None:
        """
        Validate that all required environment variables are set.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = {
            'BINANCE_API_KEY': 'Binance API key',
            'BINANCE_API_SECRET': 'Binance API secret',
            'CLAUDE_API_KEY': 'Claude API key'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables:\n" +
                "\n".join(f"  - {var}" for var in missing_vars) +
                f"\n\nPlease set these variables in your .env file."
            )


# Global configuration instance
config_loader = ConfigLoader()


def get_config() -> Dict[str, Any]:
    """Get the global configuration."""
    return config_loader.load()


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific configuration value."""
    return config_loader.get(key, default)


def validate_config() -> None:
    """Validate the configuration."""
    config_loader.validate_required_keys()
