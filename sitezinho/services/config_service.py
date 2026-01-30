import datetime
from zoneinfo import ZoneInfo
from sitezinho.models.database import db
from sitezinho.models.appConfig import AppConfig

def get_config_value(key: str, default_value: str = None) -> str:
    """Get configuration value from database"""
    config = db.session.execute(
        db.select(AppConfig).where(AppConfig.config_key == key)
    ).scalar_one_or_none()
    
    if config:
        return config.config_value
    return default_value


def set_config_value(key: str, value: str) -> bool:
    """Set configuration value in database"""
    try:
        config = db.session.execute(
            db.select(AppConfig).where(AppConfig.config_key == key)
        ).scalar_one_or_none()
        
        if config:
            # Update existing config
            config.config_value = value
            config.updated = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
        else:
            # Create new config
            config = AppConfig(config_key=key, config_value=value)
            db.session.add(config)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        #there _should_ be an log here, but I will add after it
        #f.write(f"Error setting config {key}: {str(e)}\n")
        return False


def get_single_vote_setting() -> bool:
    """Get single vote setting from database"""
    value = get_config_value("single_vote", "True")
    return value.lower() == "true"


def get_vote_percentage_setting() -> int:
    """Get vote percentage setting from database"""
    value = get_config_value("vote_percentage", "50")
    try:
        return int(value)
    except ValueError:
        return 50


def initialize_default_configs():
    """Initialize default configuration values if they don't exist"""
    # Set default single_vote if not exists
    if not get_config_value("single_vote"):
        set_config_value("single_vote", "True")
    
    # Set default vote_percentage if not exists  
    if not get_config_value("vote_percentage"):
        set_config_value("vote_percentage", "50")