import os

class AppConfig:
    """Application configuration class"""
    DEBUG = True
    SECRET_KEY = 'your-secret-key-here'

    # Template and static folder configuration
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

    @staticmethod
    def get_date_formats():
        """Supported date formats for parsing"""
        return ['%Y-%m-%d', '%m/%d/%Y']

    @staticmethod
    def get_csv_delimiter():
        """CSV delimiter for parsing"""
        return ','

    @staticmethod
    def get_supported_file_types():
        """Supported file types for import"""
        return ['.csv']
