"""
PyRex Configuration Settings

Centralized configuration management using Pydantic Settings with TOML support.
"""

from pathlib import Path
from typing import Optional, Tuple, Type
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic_settings.sources import TomlConfigSettingsSource


class PyRexSettings(BaseSettings):
    """
    PyRex application settings with TOML configuration file support.

    Settings can be overridden via environment variables with PYREX_ prefix.
    """

    model_config = SettingsConfigDict(
        toml_file="pyrex_config.toml",
        env_prefix="PYREX_",
        case_sensitive=False,
    )

    # Text Processing Settings
    minimal_text_length: int = Field(
        default=1000,
        gt=0,
        description="Minimum text length (chars) required to process a document"
    )

    preview_text_chars: int = Field(
        default=2000,
        gt=0,
        description="Number of characters to show in console preview"
    )

    # Performance Settings
    chardet_sample_size: int = Field(
        default=32768,
        gt=0,
        description="Sample size in bytes for encoding detection"
    )

    html_detection_sample: int = Field(
        default=1024,
        gt=0,
        description="Sample size in bytes for HTML content detection"
    )

    # HTML Processing Settings
    remove_scripts: bool = Field(
        default=True,
        description="Remove script tags during HTML parsing"
    )

    remove_comments: bool = Field(
        default=True,
        description="Remove HTML comments during parsing"
    )

    remove_styles: bool = Field(
        default=True,
        description="Remove style tags during HTML parsing"
    )

    use_lxml_parser: bool = Field(
        default=True,
        description="Prefer lxml parser over html.parser for better performance"
    )

    # Text Encoding Settings
    skip_ascii_optimization: bool = Field(
        default=False,
        description="Skip ASCII optimization in text encoding repair"
    )

    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for encoding detection"
    )

    # Output Settings
    output_mode: str = Field(
        default="console",
        description="Output mode: 'console' for interactive display, 'dump' for file output"
    )

    output_directory: str = Field(
        default="output",
        description="Directory for output files (created if doesn't exist)"
    )

    dump_with_html_tags: bool = Field(
        default=False,
        description="Include HTML tags in dumped output (False for plain text only)"
    )

    show_compression_stats: bool = Field(
        default=True,
        description="Display compression ratio statistics in console output"
    )

    show_processing_stats: bool = Field(
        default=True,
        description="Display processing statistics (original vs extracted text length)"
    )

    # Debug Settings
    verbose_logging: bool = Field(
        default=False,
        description="Enable verbose logging for debugging"
    )

    # Future Extension Settings
    enable_boilerplate_detection: bool = Field(
        default=False,
        description="Enable boilerplate detection (future feature)"
    )

    enable_deduplication: bool = Field(
        default=False,
        description="Enable near-duplicate detection (future feature)"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the order and selection of settings sources.

        Returns:
            Tuple of settings sources in priority order (first wins)
        """
        return (
            init_settings,  # Highest priority: direct initialization
            env_settings,   # Second: environment variables
            TomlConfigSettingsSource(settings_cls),  # Third: TOML file
            dotenv_settings,  # Fourth: .env file
            file_secret_settings,  # Lowest: secrets
        )


# Global settings instance - loaded once on import
try:
    settings = PyRexSettings()
except Exception as e:
    # Fallback to defaults if config file is missing or invalid
    print(f"Warning: Could not load configuration file, using defaults: {e}")
    settings = PyRexSettings(_env_file=None)